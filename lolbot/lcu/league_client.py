"""
Handles all HTTP request to the local LoL Client,
providing functions for interacting with various LoL endpoints.
"""

from __future__ import annotations

import json
from typing import Any

import requests
import urllib3

from lolbot.system import cmd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LCUError(Exception):
    """Exception for LCU API errors."""


class LeagueClient:
    """Handles authenticated requests to the local League Client API."""

    def __init__(self, default_timeout: float = 2.0):
        self.client = requests.Session()
        self.client.verify = False
        self.client.headers.update({"Accept": "application/json"})
        self.client.trust_env = False

        self.default_timeout = default_timeout
        self.endpoint = ""
        self._refresh_auth()

    def _refresh_auth(self) -> None:
        self.endpoint = cmd.get_auth_string()

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.endpoint}{path}"

    def _format_request_exception(self, method: str, path: str, err: Exception) -> str:
        response = getattr(err, "response", None)
        if response is None:
            return f"{method} {path} failed: {err}"

        details = ""
        try:
            details = (response.text or "").strip()
        except Exception:
            details = ""
        if len(details) > 300:
            details = details[:300] + "..."

        if details:
            return f"{method} {path} failed [{response.status_code}]: {details}"
        return f"{method} {path} failed [{response.status_code}]: {err}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Any = None,
        timeout: float | None = None,
    ) -> requests.Response:
        url = self._build_url(path)
        timeout = self.default_timeout if timeout is None else timeout

        for attempt in range(2):
            try:
                response = self.client.request(method=method, url=url, json=json_body, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                if attempt == 0 and self._should_refresh_auth_and_retry(exc):
                    self._refresh_auth()
                    url = self._build_url(path)
                    continue
                raise LCUError(self._format_request_exception(method, path, exc)) from exc

        raise LCUError(f"{method} {path} failed after retry")

    @staticmethod
    def _maybe_json(body: Any) -> Any:
        if not isinstance(body, str):
            return body
        payload = body.strip()
        if payload == "":
            return None
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return body

    def request_raw(self, method: str, path: str, body: Any = None) -> requests.Response:
        """Public generic request helper for debug/tooling UIs (e.g. HTTP tab)."""
        return self._request(method.upper(), path, json_body=self._maybe_json(body))

    @staticmethod
    def _should_refresh_auth_and_retry(exc: requests.RequestException) -> bool:
        # Local client not reachable or handshake timed out (client restarting, port changed, etc.)
        if isinstance(
            exc,
            (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.SSLError,
            ),
        ):
            return True

        # Endpoint reached but token no longer valid / auth changed.
        response = getattr(exc, "response", None)
        if response is not None and response.status_code in (401, 403):
            return True

        return False

    def get_phase(self) -> str:
        response = self._request("GET", "/lol-gameflow/v1/gameflow-phase")
        return response.json()

    def create_lobby(self, lobby_id: int) -> None:
        self._request("POST", "/lol-lobby/v2/lobby", json_body={"queueId": lobby_id})

    def start_matchmaking(self) -> None:
        self._request("POST", "/lol-lobby/v2/lobby/matchmaking/search")

    def accept_match(self) -> None:
        self._request("POST", "/lol-matchmaking/v1/ready-check/accept")

    def get_summoner_name(self) -> str:
        response = self._request("GET", "/lol-summoner/v1/current-summoner")
        data = response.json()
        return data.get("displayName") or data.get("gameName") or ""

    def get_summoner_level(self) -> int:
        response = self._request("GET", "/lol-summoner/v1/current-summoner")
        return int(response.json().get("summonerLevel", 0))

    def get_lobby_id(self) -> int:
        response = self._request("GET", "/lol-lobby/v2/lobby")
        return int(response.json()["gameConfig"]["queueId"])

    def get_patch(self) -> str:
        response = self._request("GET", "/lol-patch/v1/game-version")
        version = response.text.strip().strip('"')
        parts = version.split(".")
        if len(parts) >= 2:
            return f"{parts[0]}.{parts[1]}"
        return version

    def get_matchmaking_time(self) -> str:
        response = self._request("GET", "/lol-matchmaking/v1/search")
        return str(int(response.json()["timeInQueue"]))

    def get_estimated_queue_time(self) -> int:
        response = self._request("GET", "/lol-matchmaking/v1/search")
        return int(response.json()["estimatedQueueTime"])

    def get_cs_time_remaining(self) -> str:
        response = self._request("GET", "/lol-champ-select/v1/session")
        return str(response.json()["timer"]["adjustedTimeLeftInPhase"])

    def restart_ux(self) -> None:
        self._request("POST", "/riotclient/kill-and-restart-ux")

    def access_token_exists(self) -> bool:
        try:
            self._request("GET", "/rso-auth/v1/authorization")
            return True
        except LCUError:
            return False

    def launch_league_from_rc(self) -> None:
        self._request(
            "POST",
            "/product-launcher/v1/products/league_of_legends/patchlines/live",
        )

    def login(self, username: str, password: str) -> None:
        self._request(
            "POST",
            "/rso-auth/v2/authorizations",
            json_body={"clientId": "riot-client", "trustLevels": ["always_trusted"]},
        )
        self._request(
            "PUT",
            "/rso-auth/v1/session/credentials",
            json_body={"username": username, "password": password, "persistLogin": False},
        )

    def logout_on_close(self) -> dict:
        response = self._request("POST", "/lol-login/v1/delete-rso-on-close")
        return response.json()

    def get_dodge_timer(self) -> int:
        response = self._request("GET", "/lol-matchmaking/v1/search")
        errors = response.json().get("errors", [])
        if errors:
            return int(errors[0].get("penaltyTimeRemaining", 0))
        return 0

    def quit_matchmaking(self) -> None:
        self._request("DELETE", "/lol-lobby/v2/lobby/matchmaking/search")

    def get_lobby(self) -> dict:
        response = self._request("GET", "/lol-lobby/v2/lobby")
        return response.json()

    def get_party_status(self) -> dict:
        response = self._request("GET", "/lol-lobby/v1/parties/player")
        return response.json()

    def set_position_preferences(self, primary: str, secondary: str) -> None:
        body = {"firstPreference": primary, "secondPreference": secondary}
        self._request(
            "PUT",
            "/lol-lobby/v1/lobby/members/localMember/position-preferences",
            json_body=body,
        )

    def get_quickplay_player_slots(self) -> list:
        response = self._request(
            "GET",
            "/lol-lobby/v1/lobby/members/localMember/player-slots",
        )
        return response.json()

    def set_quickplay_player_slots(self, player_slots: list) -> None:
        self._request(
            "PUT",
            "/lol-lobby/v1/lobby/members/localMember/player-slots",
            json_body=player_slots,
        )

    def get_owned_champions_minimal(self) -> list:
        response = self._request("GET", "/lol-champions/v1/owned-champions-minimal")
        return response.json()

    def get_champ_select_data(self) -> dict:
        response = self._request("GET", "/lol-champ-select/v1/session")
        return response.json()

    def get_available_champion_ids(self) -> list:
        response = self._request(
            "GET",
            "/lol-lobby-team-builder/champ-select/v1/pickable-champion-ids",
        )
        return response.json()

    def hover_champion(self, action_id: str, champion_id: int) -> None:
        self._request(
            "PATCH",
            f"/lol-champ-select/v1/session/actions/{action_id}",
            json_body={"championId": champion_id},
        )

    def lock_in_champion(self, action_id: str, champion_id: int) -> None:
        self._request(
            "POST",
            f"/lol-champ-select/v1/session/actions/{action_id}/complete",
            json_body={"championId": champion_id},
        )

    def game_reconnect(self) -> None:
        self._request("POST", "/lol-gameflow/v1/reconnect")

    def get_players_to_honor(self) -> list:
        response = self._request("GET", "/lol-honor-v2/v1/ballot")
        return response.json().get("eligibleAllies", [])

    def honor_player(self, summoner_id: int) -> None:
        self._request(
            "POST",
            "/lol-honor-v2/v1/honor-player",
            json_body={"summonerID": summoner_id},
        )

    def play_again(self) -> None:
        self._request("POST", "/lol-lobby/v2/play-again")

    def is_client_patching(self) -> bool:
        try:
            response = self._request(
                "GET",
                "/patcher/v1/products/league_of_legends/state",
            )
            return not response.json().get("isUpToDate", True)
        except LCUError:
            return False

    def send_chat_message(self, msg: str) -> None:
        """Send message to first non-empty conversation (bug-fixed path uses chat_id)."""
        open_chats = self._request("GET", "/lol-chat/v1/conversations").json()

        chat_id = None
        for conversation in open_chats:
            if conversation.get("gameName") != "" and conversation.get("gameTag") != "":
                continue
            chat_id = conversation.get("id")

        if chat_id is None:
            raise LCUError("POST /lol-chat/v1/conversations/{id}/messages failed: Chat ID is NULL")

        self._request(
            "POST",
            f"/lol-chat/v1/conversations/{chat_id}/messages",
            json_body={"body": msg},
        )