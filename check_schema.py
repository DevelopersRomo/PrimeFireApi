from bd.connection import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TimeOffRequests'")).fetchall()
    for row in result:
        print(row)
