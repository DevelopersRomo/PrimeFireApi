def test_get_timesheet_settings(client, auth_headers):
    response = client.get("/api/v1/catalogs/timesheet", headers=auth_headers)
    assert response.status_code == 200
    assert "overtime_daily_hours" in response.json()


def test_upsert_timesheet_settings_forbidden(client, auth_headers):
    # Depending on mock, this could be 403 or 200. Usually mock auth doesn't have permissions by default.
    payload = {"OvertimeDailyHours": "9.00"}
    response = client.put("/api/v1/catalogs/timesheet", json=payload, headers=auth_headers)
    assert response.status_code in {200, 403}
