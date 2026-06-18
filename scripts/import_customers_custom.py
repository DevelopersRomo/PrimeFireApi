import json
import os
import pathlib
import sys

# Add the parent directory to sys.path so we can import from PrimeFireApi
sys.path.append(pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent)

# Import all models to register with SQLModel

import pathlib

from sqlmodel import Session, select

from bd.connection import engine
from models.addresses import Addresses
from models.countries import Countries
from models.customers import (
    CustomerAlternateContacts,
    CustomerTypeEnum,
    Customers,
    MarketEnum,
)


def main():
    json_path = os.path.join(
        pathlib.Path(pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent).parent,
        "tableConvert.com_zjvjkq.json",
    )

    with pathlib.Path(json_path).open("r", encoding="utf-8") as f:
        data = json.load(f)

    with Session(engine) as session:
        # Default country - Rep Dom
        dr_country = session.exec(select(Countries).where(Countries.name == "Dominican Republic")).first()
        country_id = dr_country.country_id if dr_country else 1

        # We need a creator. Let's use 1.
        creator_id = 1

        processed_companies = set()

        for row in data:
            raw_customer_val = row.get("Customer", "").strip()

            if not raw_customer_val:
                continue

            # Identify if it's a job. If it has a colon, it's a job.
            if ":" in raw_customer_val:
                company_name = raw_customer_val.split(":")[0].strip()
            else:
                company_name = raw_customer_val.strip()

            if not company_name:
                company_name = row.get("Company", "").strip()

            if not company_name:
                continue

            if company_name.lower() in processed_companies:
                continue

            processed_companies.add(company_name.lower())

            # Check DB for existing
            existing = session.exec(select(Customers).where(Customers.company_name == company_name)).first()
            if existing:
                continue

            # ADDRESS
            address_1 = row.get("Bill to 3", "").strip() or row.get("Bill to 1", "").strip()
            address_2 = row.get("Bill to 4", "").strip() or row.get("Bill to 2", "").strip()

            address = Addresses(
                address_1=address_1[:200] if address_1 else "No Address",
                address_2=address_2[:200] if address_2 else None,
                city="Unknown",
                state="Unknown",
                zip_code="",
                country_id=country_id,
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            # CUSTOMER TYPE
            c_type_val = row.get("Customer Type", "").lower()
            customer_type = CustomerTypeEnum.COMMERCIAL
            if "res" in c_type_val:
                customer_type = CustomerTypeEnum.RESIDENTIAL

            # MARKET
            market = MarketEnum.COMMERCIAL
            if customer_type == CustomerTypeEnum.RESIDENTIAL:
                market = MarketEnum.INDIVIDUAL

            first_name = row.get("First Name", "").strip()[:100]
            last_name = row.get("Last Name", "").strip()[:100]

            primary_email = row.get("Main Email", "").strip()[:255]
            if not primary_email:
                primary_email = None

            primary_phone = row.get("Main Phone", "").strip()[:20]
            if not primary_phone:
                primary_phone = None

            customer = Customers(
                customer_type=customer_type,
                company_name=company_name[:200],
                first_name=first_name or None,
                last_name=last_name or None,
                market=market,
                primary_email=primary_email,
                primary_phone=primary_phone,
                primary_address_id=address.address_id,
                created_by=creator_id,
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)

            # ALTERNATE CONTACTS
            alt_contact_name = row.get("Secondary Contact", "").strip()
            alt_phone = row.get("Alt. Phone", "").strip()

            if alt_contact_name or alt_phone:
                alt = CustomerAlternateContacts(
                    customer_id=customer.customer_id,
                    name=(alt_contact_name or "Alternate Contact")[:200],
                    phone=alt_phone[:20] if alt_phone else None,
                )
                session.add(alt)

            # NOTES
            notes_chunks = []

            rnc = row.get("Bill to 2", "")
            if "RNC" in rnc:
                notes_chunks.append(rnc)

            terms = row.get("Terms", "").strip()
            if terms:
                notes_chunks.append(f"Terms: {terms}")

            credits = row.get("Credit Limit", "").strip()
            if credits:
                notes_chunks.append(f"Credit Limit: {credits}")

            rep = row.get("Rep", "").strip()
            if rep:
                notes_chunks.append(f"Rep: {rep}")

            job_desc = row.get("Job Description", "").strip()
            if job_desc:
                notes_chunks.append(f"Job Description: {job_desc}")

            if notes_chunks:
                note_text = "\n".join(notes_chunks)
                # Avoid ORM insert for CustomerNotes due to pyodbc varchar(max) bug
                from sqlalchemy import text

                stmt = text(
                    "INSERT INTO dbo.customer_notes (customer_id, note_text, created_at, created_by) "
                    "VALUES (:customer_id, :note_text, GETUTCDATE(), :created_by)"
                )
                session.execute(
                    stmt, {"customer_id": customer.customer_id, "note_text": note_text, "created_by": creator_id}
                )

            session.commit()


if __name__ == "__main__":
    main()
