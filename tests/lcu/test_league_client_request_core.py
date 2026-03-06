import requests
import pytest

from lolbot.lcu.league_client import LeagueClient, LCUError


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            err = requests.HTTPError(f"HTTP {self.status_code}")
            err.response = self
            raise err


def _make_client(monkeypatch, auth_values):
    values = iter(auth_values)
    monkeypatch.setattr(
        "lolbot.lcu.league_client.cmd.get_auth_string",
        lambda: next(values),
    )
    return LeagueClient(default_timeout=2.5)


def test_request_passes_timeout_and_builds_url(monkeypatch):
    client = _make_client(monkeypatch, ["https://riot:t1@127.0.0.1:1111"])
    calls = []

    def fake_request(**kwargs):
        calls.append(kwargs)
        return DummyResponse(status_code=200, json_data={"ok": True})

    monkeypatch.setattr(client.client, "request", fake_request)
    resp = client._request("GET", "/lol-gameflow/v1/gameflow-phase")

    assert resp.json() == {"ok": True}
    assert calls[0]["url"] == "https://riot:t1@127.0.0.1:1111/lol-gameflow/v1/gameflow-phase"
    assert calls[0]["timeout"] == 2.5


def test_request_retries_on_connection_error_and_refreshes_auth(monkeypatch):
    client = _make_client(
        monkeypatch,
        [
            "https://riot:old@127.0.0.1:1111",
            "https://riot:new@127.0.0.1:2222",
        ],
    )
    calls = []

    def fake_request(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise requests.ConnectionError("connection failed")
        return DummyResponse(status_code=200, json_data={"ok": True})

    monkeypatch.setattr(client.client, "request", fake_request)

    resp = client._request("GET", "/lol-gameflow/v1/gameflow-phase")
    assert resp.json() == {"ok": True}
    assert len(calls) == 2
    assert calls[0]["url"].startswith("https://riot:old@127.0.0.1:1111")
    assert calls[1]["url"].startswith("https://riot:new@127.0.0.1:2222")


def test_request_retries_on_401(monkeypatch):
    client = _make_client(
        monkeypatch,
        [
            "https://riot:old@127.0.0.1:1111",
            "https://riot:new@127.0.0.1:2222",
        ],
    )
    calls = []

    def fake_request(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return DummyResponse(status_code=401, text='{"errorCode":"CREDENTIALS_INVALID"}')
        return DummyResponse(status_code=200, json_data={"ok": True})

    monkeypatch.setattr(client.client, "request", fake_request)

    resp = client._request("GET", "/lol-gameflow/v1/gameflow-phase")
    assert resp.json() == {"ok": True}
    assert len(calls) == 2


def test_request_does_not_retry_on_non_auth_http_error(monkeypatch):
    client = _make_client(monkeypatch, ["https://riot:t1@127.0.0.1:1111"])
    call_count = {"n": 0}

    def fake_request(**_kwargs):
        call_count["n"] += 1
        return DummyResponse(status_code=404, text='{"message":"not found"}')

    monkeypatch.setattr(client.client, "request", fake_request)

    with pytest.raises(LCUError) as exc:
        client._request("GET", "/does-not-exist")

    assert call_count["n"] == 1
    assert "404" in str(exc.value)
