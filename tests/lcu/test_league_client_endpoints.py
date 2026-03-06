import pytest

from lolbot.lcu.league_client import LeagueClient, LCUError


class DummyResponse:
    def __init__(self, json_data=None, text=""):
        self._json_data = json_data
        self.text = text

    def json(self):
        return self._json_data


def _make_client(monkeypatch):
    monkeypatch.setattr(
        "lolbot.lcu.league_client.cmd.get_auth_string",
        lambda: "https://riot:t1@127.0.0.1:1111",
    )
    return LeagueClient()


def test_get_phase_calls_expected_endpoint(monkeypatch):
    client = _make_client(monkeypatch)
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return DummyResponse(json_data="Lobby")

    monkeypatch.setattr(client, "_request", fake_request)

    phase = client.get_phase()
    assert phase == "Lobby"
    assert calls == [("GET", "/lol-gameflow/v1/gameflow-phase", {})]


def test_create_lobby_posts_queue_id(monkeypatch):
    client = _make_client(monkeypatch)
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return DummyResponse()

    monkeypatch.setattr(client, "_request", fake_request)

    client.create_lobby(880)
    assert calls == [
        ("POST", "/lol-lobby/v2/lobby", {"json_body": {"queueId": 880}})
    ]


def test_get_dodge_timer_with_error_payload(monkeypatch):
    client = _make_client(monkeypatch)

    monkeypatch.setattr(
        client,
        "_request",
        lambda *_args, **_kwargs: DummyResponse(
            json_data={"errors": [{"penaltyTimeRemaining": 17}]}
        ),
    )

    assert client.get_dodge_timer() == 17


def test_get_dodge_timer_without_errors(monkeypatch):
    client = _make_client(monkeypatch)
    monkeypatch.setattr(
        client,
        "_request",
        lambda *_args, **_kwargs: DummyResponse(json_data={"errors": []}),
    )
    assert client.get_dodge_timer() == 0


def test_send_chat_message_uses_chat_id_in_path(monkeypatch):
    client = _make_client(monkeypatch)
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path == "/lol-chat/v1/conversations":
            return DummyResponse(
                json_data=[
                    {"id": "pvp-chat", "gameName": "", "gameTag": ""},
                ]
            )
        return DummyResponse(json_data={})

    monkeypatch.setattr(client, "_request", fake_request)
    client.send_chat_message("hello")

    assert calls[0][1] == "/lol-chat/v1/conversations"
    assert calls[1][0] == "POST"
    assert calls[1][1] == "/lol-chat/v1/conversations/pvp-chat/messages"
    assert calls[1][2]["json_body"] == {"body": "hello"}


def test_send_chat_message_raises_if_no_chat_id(monkeypatch):
    client = _make_client(monkeypatch)
    monkeypatch.setattr(
        client,
        "_request",
        lambda *_args, **_kwargs: DummyResponse(
            json_data=[{"id": "x", "gameName": "Some", "gameTag": "Tag"}]
        ),
    )

    with pytest.raises(LCUError):
        client.send_chat_message("hello")


def test_get_patch_parsing(monkeypatch):
    client = _make_client(monkeypatch)
    monkeypatch.setattr(
        client,
        "_request",
        lambda *_args, **_kwargs: DummyResponse(text='"16.5.1"'),
    )
    assert client.get_patch() == "16.5"
