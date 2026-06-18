import json
import os
import pathlib
import sys

# Add the parent directory to sys.path so we can import from PrimeFireApi
sys.path.append(pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent)

from sqlmodel import Session, select

from bd.connection import engine
from models.addresses import Addresses
from models.countries import Countries
from models.customers import CustomerAlternateContacts, CustomerNotes, CustomerTypeEnum, Customers
from models.employees import Employees


def normalize_customer_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    if ":" in raw_name:
        return raw_name.split(":", maxsplit=1)[0].strip()
    return raw_name.strip()


def import_customers():
    json_path = os.path.join(
        pathlib.Path(pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent).parent,
        "tableConvert.com_zjvjkq.json",
    )

    with pathlib.Path(json_path).open(encoding="utf-8") as f:
        data = json.load(f)

    with Session(engine) as session:
        # Get a default employee for created_by
        system_user = session.exec(select(Employees).first()).first()
        created_by_id = system_user.employee_id if system_user else 1

        # Get a default country for addresses
        default_country = session.exec(select(Countries).first()).first()
        country_id = default_country.country_id if default_country else 1

        processed_companies = set()
        processed_emails = set()

        for row in data:
            raw_customer = row.get("Customer", "")
            if not raw_customer:
                continue

            company_name = normalize_customer_name(raw_customer)
            if not company_name:
                company_name = row.get("Company", "Unknown Company").strip()

            email = row.get("Main Email", "").strip()

            # Check for duplicates
            if company_name in processed_companies:
                continue
            if email and email in processed_emails:
                continue

            # Also check database to avoid inserting dupes repeatedly across script runs
            existing = session.exec(select(Customers).where(Customers.company_name == company_name)).first()
            if existing:
                processed_companies.add(company_name)
                if email:
                    processed_emails.add(email)
                continue

            # Parse Address
            # Just do a best effort based on Ship to or Bill to
            address_text_1 = row.get("Bill to 3", "").strip() or row.get("Ship to 3", "").strip() or "N/A"
            address_text_2 = row.get("Bill to 4", "").strip() or row.get("Ship to 4", "").strip()

            address = Addresses(
                address_1=address_text_1[:200],
                address_2=address_text_2[:200] if address_text_2 else None,
                city="Unknown",
                state="Unknown",
                zip_code="00000",
                country_id=country_id,
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            first_name = row.get("First Name", "").strip()
            last_name = row.get("Last Name", "").strip()
            phone = row.get("Main Phone", "").strip()

            customer_type_str = row.get("Customer Type", "").strip().lower()
            customer_type = CustomerTypeEnum.COMMERCIAL
            if customer_type_str == "residential":
                customer_type = CustomerTypeEnum.RESIDENTIAL

            customer = Customers(
                customer_type=customer_type,
                company_name=company_name[:200],
                first_name=first_name[:100] if first_name else None,
                last_name=last_name[:100] if last_name else None,
                primary_email=email[:255] if email else None,
                primary_phone=phone[:20] if phone else None,
                primary_address_id=address.address_id,
                created_by=created_by_id,
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)

            processed_companies.add(company_name)
            if email:
                processed_emails.add(email)

            # Alternate Contacts
            alt_phone = row.get("Alt. Phone", "").strip()
            secondary_contact = row.get("Secondary Contact", "").strip()
            if alt_phone or secondary_contact:
                alt_contact = CustomerAlternateContacts(
                    customer_id=customer.customer_id,
                    name=(secondary_contact or "Alternate Contact")[:200],
                    phone=alt_phone[:20] if alt_phone else None,
                )
                session.add(alt_contact)

            # Notes
            job_desc = row.get("Job Description", "").strip()
            terms = row.get("Terms", "").strip()
            note_content = []
            if job_desc:
                note_content.append(f"Job Description: {job_desc}")
            if terms:
                note_content.append(f"Terms: {terms}")

            if note_content:
                note = CustomerNotes(
                    customer_id=customer.customer_id, note_text="\\n".join(note_content), created_by=created_by_id
                )
                session.add(note)

            session.commit()


if __name__ == "__main__":
    import_customers()
