from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_subprocess_run():
    with patch("api.backups.subprocess.run") as mock_run:
        yield mock_run


@pytest.fixture
def mock_os_listdir():
    with patch("api.backups.os.listdir") as mock_listdir:
        yield mock_listdir


@pytest.fixture
def mock_pathlib_exists():
    with patch("api.backups.pathlib.Path.exists") as mock_exists:
        yield mock_exists


def test_trigger_backup_success_all(client, auth_headers, mock_subprocess_run, mock_os_listdir):
    # Mock subprocess.run to return success
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Backup OK"
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    # Mock os.listdir to pretend some sql files were created
    mock_os_listdir.return_value = ["backup_20260314_db.sql", "backup_20260314_primefiredb.sql"]

    # We need to mock datetime within api.backups or just let it use current date, and we configure the mock listdir to match today's date format
    from datetime import datetime

    today = datetime.now().strftime("%Y%m%d")
    mock_os_listdir.return_value = [f"backup_{today}_db.sql", f"backup_{today}_primefiredb.sql"]

    response = client.post("/backups/trigger?db_prefix=all", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "completed successfully" in data["message"]
    # 2 calls to subprocess run, one for DB and one for PRIMEFIRE_DB
    assert mock_subprocess_run.call_count == 2


def test_trigger_backup_failure(client, auth_headers, mock_subprocess_run, mock_os_listdir):
    # Mock subprocess.run to return failure
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error during backup"
    mock_subprocess_run.return_value = mock_result

    mock_os_listdir.return_value = []

    response = client.post("/backups/trigger?db_prefix=DB", headers=auth_headers)
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert "Backup error" in data["message"]
    assert mock_subprocess_run.call_count == 1


def test_trigger_backup_structure_only(client, auth_headers, mock_subprocess_run, mock_os_listdir):
    # Mock subprocess.run to return success
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Backup OK"
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    from datetime import datetime

    today = datetime.now().strftime("%Y%m%d")
    mock_os_listdir.return_value = [f"complete_backup_db_structure_{today}_120000.sql"]

    response = client.post("/backups/trigger?db_prefix=DB&backup_type=structure", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify --type structure was passed to the script
    call_args = mock_subprocess_run.call_args[0][0]
    assert "--type" in call_args
    assert "structure" in call_args


def test_trigger_backup_invalid_type(client, auth_headers, mock_subprocess_run, mock_os_listdir):
    response = client.post("/backups/trigger?db_prefix=DB&backup_type=invalid", headers=auth_headers)
    assert response.status_code == 422


def test_get_backup_status(client, auth_headers, mock_pathlib_exists, mock_os_listdir):
    mock_pathlib_exists.return_value = True
    # The status endpoint also calls stat on the files to order them
    with patch("api.backups.pathlib.Path.stat") as mock_stat:
        mock_stat_ret = MagicMock()
        mock_stat_ret.st_mtime = 1234567890
        mock_stat.return_value = mock_stat_ret

        mock_os_listdir.return_value = ["old_backup.sql", "new_backup.sql"]

        response = client.get("/backups/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert "backup_dir" in data
        assert len(data["recent_backups"]) == 2
