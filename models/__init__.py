import models.it as it  # noqa: F401  (registers IT schema tables in SQLModel metadata)
from models.auth_tokens import AuthToken as AuthToken
from models.auth_tokens import RevokedSession as RevokedSession
from models.auth_tokens import UserSessionVersion as UserSessionVersion
from models.tickets import (
    TicketRecurrenceConfig as TicketRecurrenceConfig,
)
from models.tickets import (
    TicketRecurrenceType as TicketRecurrenceType,
)
from models.tickets import (
    TicketType as TicketType,
)
from models.tickets import (
    Tickets as Tickets,
)
