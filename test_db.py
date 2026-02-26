import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

try:
    response = client.get("/api/v1/timesheet?view=day&start_date=2026-02-22&end_date=2026-02-28&skip=0&limit=20", headers={"X-Tenant-ID": "1"})
    print(response.status_code)
    print(response.json())
except Exception as e:
    import traceback
    traceback.print_exc()
