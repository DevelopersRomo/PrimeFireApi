import asyncio
from datetime import datetime, timedelta
from typing import Optional
import logging

from sqlmodel import Session, select
from core.microsoft_graph import graph_client
from models.employees import Employees
from models.countries import Countries
from bd.connection import engine

logger = logging.getLogger(__name__)

def normalize_country_to_code(country_name: str) -> Optional[str]:
    """
    Convert country names or codes to standard ISO 3166-1 alpha-2 codes.
    """
    if not country_name or not country_name.strip():
        return None

    country_name = country_name.strip().upper()

    # Direct mapping for common countries
    country_map = {
        # United States variations
        'UNITED STATES': 'US',
        'USA': 'US',
        'UNITED STATES OF AMERICA': 'US',
        'US': 'US',
        'AMERICA': 'US',

        # Puerto Rico
        'PUERTO RICO': 'PR',
        'PR': 'PR',

        # Dominican Republic variations
        'REPÚBLICA DOMINICANA': 'DO',
        'DOMINICAN REPUBLIC': 'DO',
        'REPUBLICA DOMINICANA': 'DO',
        'DO': 'DO',

        # Mexico
        'MEXICO': 'MX',
        'MÉXICO': 'MX',
        'MX': 'MX',

        # Add more countries as needed
        'CANADA': 'CA',
        'SPAIN': 'ES',
        'FRANCE': 'FR',
        'GERMANY': 'DE',
        'ITALY': 'IT',
        'UNITED KINGDOM': 'GB',
        'UK': 'GB',
    }

    return country_map.get(country_name)

async def get_or_create_country_id(db: Session, country_input: str) -> tuple[Optional[int], bool]:
    """
    Get CountryId for a country name/code, creating it if it doesn't exist.
    Always stores standardized ISO codes.
    Returns (CountryId, was_created) tuple.
    CountryId is None if country_input is None or empty.
    """
    if not country_input or not country_input.strip():
        return None, False

    # Normalize to standard ISO code
    country_code = normalize_country_to_code(country_input.strip())
    if not country_code:
        return None, False

    # Try to find existing country by code
    existing_country = db.exec(
        select(Countries).filter(Countries.Name == country_code)
    ).first()

    if existing_country:
        return existing_country.CountryId, False

    # Create new country with ISO code
    new_country = Countries(Name=country_code)
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country.CountryId, True

def is_primefire_domain(email: str) -> bool:
    """
    Check if email belongs to PrimeFire domains
    Only checks the domain part (after @)
    Accepts domains like: primefire.us, primefire.do, sub.primefire.com, etc.
    """
    if not email:
        return False

    # Extract domain from email (part after @)
    domain = email.lower().split('@')[-1] if '@' in email else ''

    # Check if domain contains primefire as a separate segment
    # This avoids false positives like "notprimefire.com"
    domain_parts = domain.split('.')
    return any('primefire' == part for part in domain_parts)

def get_country_id_from_domain(email: str) -> Optional[int]:
    """
    LEGACY: Determine CountryId based on email domain
    Now we filter by PrimeFire domains and get country from Graph
    """
    if not email:
        return None

    domain = email.lower().split('@')[-1] if '@' in email else ''

    if domain.endswith('.us'):
        return 1  # Puerto Rico
    elif domain.endswith('.do'):
        return 2  # República Dominicana

    return None  # Skip other domains

class EmployeeSyncScheduler:
    """Background task scheduler for Microsoft 365 employee synchronization"""
    
    def __init__(self):
        self.is_running = False
        self.last_sync: Optional[datetime] = None
        self.sync_interval_hours = 24  # Sync every 24 hours by default
        self._task: Optional[asyncio.Task] = None
    
    async def sync_employees_from_microsoft(self) -> dict:
        """
        Sync all employees from Microsoft 365 to local database
        Returns sync statistics
        """
        try:
            logger.info("🔄 Starting automatic sync from Microsoft 365...")
            
            ms_users = await graph_client.get_all_users()
            
            stats = {
                "total_ms_users": len(ms_users),  # Total users from Microsoft Graph
                "primefire_users": 0,  # Users with PrimeFire domains
                "processed": 0,  # Successfully processed PrimeFire users
                "created": 0,
                "updated": 0,
                "errors": 0,
                "countries_created": 0,
                "timestamp": datetime.now()
            }
            
            with Session(engine) as db:
                for ms_user in ms_users:
                    try:
                        # Filter only PrimeFire domains
                        email = ms_user.get("userPrincipalName") or ms_user.get("mail")
                        if not email or not is_primefire_domain(email):
                            # Debug: log skipped users
                            logger.debug(f"⏭️ Skipping user {email} - not PrimeFire domain")
                            continue  # Skip non-PrimeFire users

                        stats["primefire_users"] += 1
                        logger.debug(f"✅ Processing PrimeFire user: {email}")

                        # Get country from Graph user data
                        graph_country = ms_user.get("country")
                        country_id, country_created = await get_or_create_country_id(db, graph_country) if graph_country else (None, False)

                        if country_created:
                            stats["countries_created"] += 1

                        employee_data = graph_client.map_graph_user_to_employee(ms_user)
                        employee_data["LastSyncedAt"] = datetime.now()
                        employee_data["CountryId"] = country_id

                        stats["processed"] += 1

                        # Check if employee exists by AzureOid
                        existing = db.exec(
                            select(Employees).filter(Employees.AzureOid == employee_data["AzureOid"])
                        ).first()

                        if existing:
                            # Update existing employee
                            for key, value in employee_data.items():
                                if value is not None:
                                    setattr(existing, key, value)
                            stats["updated"] += 1
                        else:
                            # Create new employee
                            new_employee = Employees(**employee_data)
                            db.add(new_employee)
                            stats["created"] += 1

                        db.commit()

                    except Exception as e:
                        stats["errors"] += 1
                        continue
            
            self.last_sync = datetime.now()
            
            return stats
        
        except Exception as e:
            logger.error(f"❌ Failed to sync from Microsoft 365: {e}")
            raise
    
    async def _periodic_sync_loop(self):
        """Background loop that runs periodic syncs"""
        while self.is_running:
            try:
                # Check if it's time to sync
                should_sync = (
                    self.last_sync is None or 
                    datetime.now() - self.last_sync >= timedelta(hours=self.sync_interval_hours)
                )
                
                if should_sync:
                    await self.sync_employees_from_microsoft()
                
                # Wait 1 hour before checking again
                await asyncio.sleep(3600)
            
            except asyncio.CancelledError:
                logger.info("🛑 Sync scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in sync loop: {e}")
                await asyncio.sleep(3600)  # Wait before retrying
    
    async def start_periodic_sync(self, interval_hours: int = 24):
        """
        Start periodic background sync
        
        Args:
            interval_hours: Hours between syncs (default: 24)
        """
        if self.is_running:
            logger.warning("⚠️ Sync scheduler already running")
            return
        
        self.sync_interval_hours = interval_hours
        self.is_running = True
        
        logger.info(f"🚀 Starting periodic sync (every {interval_hours} hours)")
        
        # Run initial sync immediately
        try:
            await self.sync_employees_from_microsoft()
        except Exception as e:
            logger.error(f"❌ Initial sync failed: {e}")
        
        # Start background loop
        self._task = asyncio.create_task(self._periodic_sync_loop())
    
    async def stop_periodic_sync(self):
        """Stop periodic background sync"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 Sync scheduler stopped")
    
    async def sync_on_startup(self):
        """
        Run a one-time sync on application startup
        Recommended for simpler use cases
        """
        logger.info("🚀 Running startup sync from Microsoft 365...")
        
        try:
            stats = await self.sync_employees_from_microsoft()
            logger.info(f"✅ Startup sync completed: {stats}")
            return stats
        except Exception as e:
            logger.error(f"❌ Startup sync failed: {e}")
            # Don't fail the application if sync fails
            return None

# Singleton instance
sync_scheduler = EmployeeSyncScheduler()

