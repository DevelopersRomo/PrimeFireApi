"""Send a real test email through a named mail profile.

Bypasses the HTTP layer on purpose: the contact endpoint requires a Cloudflare
Turnstile token, which is impractical locally, and the thing worth testing here
is which Microsoft tenant actually issues the message.

Run from the PrimeFireApi root so .env is picked up:

    # inspect config without sending anything
    venv/Scripts/python.exe scripts/send_test_email.py --to you@gmail.com --profile devromo_tenant --dry-run

    # send for real, one per tenant
    venv/Scripts/python.exe scripts/send_test_email.py --to you@gmail.com --profile devromo_tenant
    venv/Scripts/python.exe scripts/send_test_email.py --to you@gmail.com --profile primefire_tenant

    # exercise the full chain: site URL -> tenant_logos -> tenants.mail_profile
    venv/Scripts/python.exe scripts/send_test_email.py --to you@gmail.com --tenant-url https://devromo.com
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import settings  # noqa: E402
from core.mail_profiles import (  # noqa: E402
    DEFAULT_MAIL_PROFILE,
    env_var_names,
    get_mail_credentials,
    normalize_profile_key,
)
from services.notifications.auth import get_auth_client  # noqa: E402
from services.notifications.email_functions import send_outlook_email  # noqa: E402


def _mask(value: str) -> str:
    return f"{value[:6]}...{value[-4:]}" if len(value) > 12 else "***"


def _resolve_from_db(tenant_url: str) -> str:
    """Resolve the profile the way the real endpoint does. Needs the main DB."""
    import main  # noqa: F401  # configures every SQLModel mapper

    from bd.dependencies import SessionLocal
    from services.notifications.mail_profile import resolve_mail_profile

    with SessionLocal() as db:
        return resolve_mail_profile(db, tenant_url=tenant_url)


def _report(profile: str) -> bool:
    """Print what this profile resolves to. Returns True when it has its own tenant."""
    key = normalize_profile_key(profile)
    credentials = get_mail_credentials(key)

    print(f"  profile key : {key}")
    if credentials:
        print(f"  source      : {', '.join(env_var_names(key))}")
        print(f"  azure tenant: {credentials.tenant_id}")
        print(f"  client id   : {_mask(credentials.client_id)}")
        print(f"  sends as    : {credentials.bot_email}")
    else:
        reason = "reserved default key" if key == DEFAULT_MAIL_PROFILE else "env block missing or incomplete"
        print(f"  source      : legacy MICROSOFT_* ({reason})")
        print(f"  azure tenant: {get_auth_client(key).tenant_id}")
        print(f"  sends as    : {settings.BOT_EMAIL or '<BOT_EMAIL not set>'}")
    return credentials is not None


async def _check_sender(profile: str) -> int:
    """Ask Graph what it knows about the profile's sender mailbox."""
    import httpx

    key = normalize_profile_key(profile)
    credentials = get_mail_credentials(key)
    address = credentials.bot_email if credentials else settings.BOT_EMAIL
    if not address:
        print("No sender address configured for this profile.")
        return 1

    headers = await get_auth_client(key).get_auth_headers()
    if not headers:
        print("Could not get a token - check the tenant id, client id and secret.")
        return 1
    print("Token OK, so the credentials are valid.\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"https://graph.microsoft.com/v1.0/users/{address}"
        params = {"$select": "id,userPrincipalName,mail,displayName,accountEnabled,proxyAddresses"}
        response = await client.get(url, headers=headers, params=params)

        if response.status_code == 403:
            print("Graph refused the directory lookup (403) - the app only has Mail.Send.")
            print("That is the correct, least-privilege setup, so verify the mailbox by hand instead:")
            print("  admin.exchange.microsoft.com -> Recipients -> Mailboxes")
            print(f"  If {address} is not listed there, it is not a mailbox and cannot send.")
            print("  Check Recipients -> Groups too: distribution lists receive mail but cannot send it.")
            print("Granting User.Read.All just to run this check is not worth it.")
            return 1

        if response.status_code == 404:
            print(f"Graph does not resolve {address!r} as a user in this tenant.")
            print("Most likely it is an alias rather than the userPrincipalName, or it lives")
            print("in a different tenant. Set _BOT_EMAIL to the exact UPN.")
            return 1

        if response.status_code != 200:
            print(f"Unexpected response {response.status_code}: {response.text[:400]}")
            return 1

        user = response.json()
        print(f"  displayName        : {user.get('displayName')}")
        print(f"  userPrincipalName  : {user.get('userPrincipalName')}")
        print(f"  mail               : {user.get('mail')}")
        print(f"  accountEnabled     : {user.get('accountEnabled')}")
        print(f"  proxyAddresses     : {user.get('proxyAddresses')}")

        upn = (user.get("userPrincipalName") or "").lower()
        if upn and upn != address.lower():
            print(f"\n>>> Configured address is not the UPN. Use {user.get('userPrincipalName')!r} instead.")

        if not user.get("mail"):
            print("\n>>> 'mail' is empty, which means no Exchange Online mailbox.")
            print(">>> Assign a license, or convert the account to a shared mailbox.")

        licenses = await client.get(
            f"https://graph.microsoft.com/v1.0/users/{user['id']}/licenseDetails", headers=headers
        )
        if licenses.status_code == 200:
            skus = [item.get("skuPartNumber") for item in licenses.json().get("value", [])]
            print(f"  licenses           : {skus or 'none (fine only if this is a shared mailbox)'}")

    return 0


async def main_async(args: argparse.Namespace) -> int:
    profile = _resolve_from_db(args.tenant_url) if args.tenant_url else args.profile

    if args.tenant_url:
        print(f"\nResolved {args.tenant_url} through the database:")
    else:
        print(f"\nUsing profile {args.profile!r} directly:")
    _report(profile)

    if args.check_sender:
        print()
        return await _check_sender(profile)

    if args.dry_run:
        print("\nDry run, nothing sent.")
        return 0

    if not args.to:
        print("\nNothing sent: pass --to with a recipient address.")
        return 1

    key = normalize_profile_key(profile)
    if not get_mail_credentials(key) and not settings.BOT_EMAIL:
        print("\nFAILED - this profile falls back to BOT_EMAIL, which is not set in .env")
        return 1

    subject = f"PrimeFire mail profile test - {key}"
    body = (
        f"<p>Test message routed through the <strong>{key}</strong> mail profile.</p>"
        f"<p>If the From address above is not what you expected, check the "
        f"<code>[SEND_OUTLOOK_EMAIL]</code> log line.</p>"
    )

    print(f"\nSending to {args.to} ...")
    success, message_id, error = await send_outlook_email(
        send_as_email=settings.BOT_EMAIL,
        to_emails=[args.to],
        subject=subject,
        body=body,
        mail_profile=key,
    )

    if success:
        print(f"OK - sent (message id {message_id})")
        return 0

    print(f"FAILED - {error}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--to", help="Recipient address (not needed with --dry-run or --check-sender)")
    parser.add_argument("--profile", default=DEFAULT_MAIL_PROFILE, help="Mail profile key, e.g. devromo_tenant")
    parser.add_argument("--tenant-url", help="Resolve the profile from the database using this site URL")
    parser.add_argument("--dry-run", action="store_true", help="Report the resolved config without sending")
    parser.add_argument(
        "--check-sender", action="store_true", help="Ask Graph whether the sender mailbox actually exists"
    )
    return asyncio.run(main_async(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
