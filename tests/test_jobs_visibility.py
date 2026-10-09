from models.jobs import Jobs


def test_full_jobs_list_requires_jobs_can_view(client, db_session, auth_headers, permission_override):
    permission_override("jobs", set())
    db_session.add(Jobs(title="Private job", status="draft"))
    db_session.commit()

    response = client.get("/jobs", headers=auth_headers)

    assert response.status_code == 403


def test_non_active_job_status_requires_jobs_can_view(client, db_session, auth_headers, permission_override):
    db_session.add(Jobs(title="Private job", status="draft"))
    db_session.commit()
    permission_override("jobs", set())

    response = client.get("/jobs/status/draft", headers=auth_headers)

    assert response.status_code == 403


def test_active_job_status_and_public_list_remain_anonymous(client, db_session):
    active = Jobs(title="Public job", status="active")
    db_session.add(active)
    db_session.commit()

    status_response = client.get("/jobs/status/active")
    public_response = client.get("/jobs/public")

    assert status_response.status_code == 200
    assert [job["job_id"] for job in status_response.json()] == [active.job_id]
    assert public_response.status_code == 200
    assert [job["job_id"] for job in public_response.json()["items"]] == [active.job_id]


def test_job_detail_remains_anonymous(client, db_session):
    job = Jobs(title="Public job detail", status="draft")
    db_session.add(job)
    db_session.commit()

    response = client.get(f"/jobs/{job.job_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "draft"
