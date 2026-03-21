from models.countries import Countries


def test_get_countries(client, db_session, auth_headers):
    # Add multiple countries - some valid (2-char ISO codes) and some not
    countries = [
        Countries(name="US", country_id=1),
        Countries(name="MX", country_id=2),
        Countries(name="Canada", country_id=3),  # Not 2-char, should be filtered
    ]
    for country in countries:
        db_session.add(country)
    db_session.commit()

    response = client.get("/countries", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should only return 2-char ISO codes
    assert len(data) == 2
    names = [c["name"] for c in data]
    assert "US" in names
    assert "MX" in names
    assert "Canada" not in names
