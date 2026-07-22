"""API tests for IT catalog categories and items."""


class TestCategories:
    def test_create_and_list(self, client, auth_headers) -> None:
        response = client.post(
            "/it/catalog/categories/",
            json={"name": "Web Development", "item_type": "SERVICE"},
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        category = response.json()
        assert category["name"] == "Web Development"
        assert category["tenant_id"] == 1

        listed = client.get("/it/catalog/categories/", headers=auth_headers)
        assert listed.status_code == 200
        assert any(c["category_id"] == category["category_id"] for c in listed.json())

    def test_invalid_item_type_rejected(self, client, auth_headers) -> None:
        response = client.post(
            "/it/catalog/categories/",
            json={"name": "Bad", "item_type": "NOT_A_TYPE"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_soft_delete(self, client, auth_headers) -> None:
        created = client.post(
            "/it/catalog/categories/",
            json={"name": "Temporary"},
            headers=auth_headers,
        ).json()

        deleted = client.delete(f"/it/catalog/categories/{created['category_id']}", headers=auth_headers)
        assert deleted.status_code == 200
        assert deleted.json()["is_active"] is False

        active_only = client.get("/it/catalog/categories/", headers=auth_headers).json()
        assert all(c["category_id"] != created["category_id"] for c in active_only)


class TestCatalogItems:
    def test_create_service_item(self, client, auth_headers, catalog_item_payload) -> None:
        payload = {
            **catalog_item_payload,
            "service_details": {"estimated_delivery_days": 30, "deliverables": "- Responsive website"},
        }
        response = client.post("/it/catalog/items/", json=payload, headers=auth_headers)
        assert response.status_code == 201, response.text
        item = response.json()
        assert item["name"] == "Website Development"
        assert item["service_details"]["estimated_delivery_days"] == 30

    def test_filters(self, client, auth_headers, catalog_item_payload) -> None:
        client.post("/it/catalog/items/", json=catalog_item_payload, headers=auth_headers)
        client.post(
            "/it/catalog/items/",
            json={
                "item_type": "HOSTING",
                "name": "Managed Hosting",
                "billing_cycle": "ANNUAL",
                "unit_price": "150.00",
            },
            headers=auth_headers,
        )

        services = client.get("/it/catalog/items/?item_type=SERVICE", headers=auth_headers).json()
        assert all(i["item_type"] == "SERVICE" for i in services)

        annual = client.get("/it/catalog/items/?billing_cycle=ANNUAL", headers=auth_headers).json()
        assert all(i["billing_cycle"] == "ANNUAL" for i in annual)

        searched = client.get("/it/catalog/items/?search=hosting", headers=auth_headers).json()
        assert any("Hosting" in i["name"] for i in searched)

    def test_invalid_billing_cycle_rejected(self, client, auth_headers, catalog_item_payload) -> None:
        payload = {**catalog_item_payload, "billing_cycle": "WEEKLY"}
        response = client.post("/it/catalog/items/", json=payload, headers=auth_headers)
        assert response.status_code == 422

    def test_soft_delete(self, client, auth_headers, catalog_item_payload) -> None:
        item = client.post("/it/catalog/items/", json=catalog_item_payload, headers=auth_headers).json()
        deleted = client.delete(f"/it/catalog/items/{item['catalog_item_id']}", headers=auth_headers)
        assert deleted.status_code == 200
        assert deleted.json()["is_active"] is False

    def test_license_convenience_routes(self, client, auth_headers) -> None:
        response = client.post(
            "/it/licenses/",
            json={
                "item_type": "LICENSE",
                "name": "Microsoft 365 Business Premium",
                "billing_cycle": "ANNUAL",
                "unit_price": "264.00",
                "license_details": {"vendor": "Microsoft", "license_type": "PER_USER", "term_months": 12},
            },
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        item = response.json()
        assert item["item_type"] == "LICENSE"
        assert item["license_details"]["vendor"] == "Microsoft"

        listed = client.get("/it/licenses/", headers=auth_headers).json()
        assert all(i["item_type"] == "LICENSE" for i in listed)
