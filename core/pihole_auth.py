import time
import atexit
import logging
import requests
from threading import Thread
from typing import Optional, Dict, Tuple

from core.config import ENDPOINTS, PIHOLE_PASS, APIs

logger = logging.getLogger("app")

def cleanup_sessions(pihole_auth_instance):
    logger.info("Application shutting down. Ending active Pihole sessions...")
    for ep in pihole_auth_instance.endpoints:
        pihole_auth_instance._end_session(ep)

class InternalSession:
    """Holds the necessary session details for Pi-hole API calls."""
    def __init__(self, sid: str, csrf: str, validity: int):
        self.sid = sid
        self.csrf = csrf
        self.validity = validity

class PiholeAuth:
    """Manages authentication sessions for multiple Pi-hole endpoints."""
    def __init__(self, endpoints: list):
        self.endpoints = endpoints
        self.sessions: Dict[str, Optional[InternalSession]] = {} 
        self.validities: Dict[str, Optional[int]] = {}

        for ep in endpoints:
            self.sessions[ep], self.validities[ep] = self._start_session(ep)

        logger.info("Pihole sessions started")
        self._run()

    def _start_session(self, endpoint: str) -> Tuple[Optional[InternalSession], Optional[int]]:
        """Starts a new authenticated session with a Pi-hole instance."""
        if not PIHOLE_PASS:
            logger.error(f"Cannot start session for {endpoint}: PIHOLE_PASS not set.")
            return None, None
            
        url = f"{endpoint}{APIs.AUTH.value}"
        try:
            response = requests.post(url, json={"password": PIHOLE_PASS})
            if response.status_code == 200:
                data = response.json().get("session", {})
                if data:
                    session = InternalSession(data["sid"], data["csrf"], data["validity"]) 
                    return session, data["validity"]
            
            logger.error(f"Could not start session for {endpoint}: {response.status_code}")
            return None, None
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception during start_session for {endpoint}: {e}")
            return None, None

    def _end_session(self, endpoint: str):
        """Ends an active session with a Pi-hole instance."""
        url = f"{endpoint}{APIs.AUTH.value}"
        session = self.sessions.get(endpoint)

        if session is None:
            return

        headers = {
            "X-FTL-SID": session.sid,
            "X-FTL-CSRF": session.csrf
        }

        try:
            response = requests.delete(url, headers=headers) 
            if response.status_code != 204:
                logger.warn(f"Failed to gracefully end session for {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.warn(f"Exception during _end_session for {endpoint}: {e}")

    def _refresh_session(self):
        """Background thread logic to refresh all active Pi-hole sessions before they expire."""
        while True:
            valid_values = [v for v in self.validities.values() if v]

            if not valid_values:
                time.sleep(5)
                continue

            min_valid = min(valid_values)
            sleep_time = max(1, min_valid - 1)
            time.sleep(sleep_time)

            for ep in self.endpoints:
                self._end_session(ep)
                session, validity = self._start_session(ep)

                if session:
                    self.sessions[ep] = session
                    self.validities[ep] = validity
                    logger.info(f"Refreshed session for {ep}")
                else:
                    logger.warn(f"Failed to refresh {ep}, leaving old session data active")

    def _run(self):
        """Starts the background session refresh thread."""
        refresh_thread = Thread(target=self._refresh_session, daemon=True)
        refresh_thread.start()

pihole_auth = PiholeAuth(ENDPOINTS)
atexit.register(cleanup_sessions, pihole_auth)
