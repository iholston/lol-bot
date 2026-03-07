import json

from lolbot.common import accounts


def _set_account_path(monkeypatch, tmp_path):
    account_path = tmp_path / "accounts.json"
    monkeypatch.setattr(accounts, "ACCOUNT_PATH", str(account_path))
    return account_path


def test_save_or_add_appends_new_account_when_other_accounts_exist(monkeypatch, tmp_path):
    account_path = _set_account_path(monkeypatch, tmp_path)
    account_path.write_text(
        json.dumps([
            {"username": "existing", "password": "pw1", "level": 10},
        ])
    )

    accounts.save_or_add({"username": "new-user", "password": "pw2", "level": 1})

    saved = json.loads(account_path.read_text())
    assert len(saved) == 2
    assert saved[0]["username"] == "existing"
    assert saved[1] == {"username": "new-user", "password": "pw2", "level": 1}


def test_save_or_add_updates_existing_account_without_duplication(monkeypatch, tmp_path):
    account_path = _set_account_path(monkeypatch, tmp_path)
    account_path.write_text(
        json.dumps([
            {"username": "same-user", "password": "old", "level": 3},
        ])
    )

    accounts.save_or_add({"username": "same-user", "password": "new", "level": 7})

    saved = json.loads(account_path.read_text())
    assert len(saved) == 1
    assert saved[0] == {"username": "same-user", "password": "new", "level": 7}


def test_save_or_add_adds_account_when_file_missing(monkeypatch, tmp_path):
    account_path = _set_account_path(monkeypatch, tmp_path)

    accounts.save_or_add({"username": "first", "password": "pw", "level": 0})

    saved = json.loads(account_path.read_text())
    assert saved == [{"username": "first", "password": "pw", "level": 0}]
