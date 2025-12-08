import os
import logging
from enum import Enum

logger = logging.getLogger("app")

if 'ENDPOINTS' in os.environ:
    endpoints_raw = os.environ['ENDPOINTS']
    ENDPOINTS = [e.strip().rstrip("/") for e in endpoints_raw.split(",") if e.strip()]
else:
    logger.error("No ENDPOINTS env variable set. Setting to localhost")
    ENDPOINTS = []
logger.info(f"Pi-Hole API host set to {ENDPOINTS}")

PIHOLE_PASS = os.environ.get('PIHOLE_PASS')
if not PIHOLE_PASS:
    logger.error("No PIHOLE_PASS env variable set.")

try:
    ADBLOCK_GROUP_ID = int(os.environ.get('ADBLOCK_GROUP_ID'))
except ValueError:
    logger.warn("ADBLOCK_GROUP_ID is not an integer. Defaulting to 0.")
    ADBLOCK_GROUP_ID = 0

try:
    NON_ADBLOCK_GROUP_ID = int(os.environ.get('NON_ADBLOCK_GROUP_ID'))
except ValueError:
    logger.warn("NON_ADBLOCK_GROUP_ID is not an integer. Defaulting to 1.")
    NON_ADBLOCK_GROUP_ID = 1

logger.info(f"Ad-Block Group ID set to {ADBLOCK_GROUP_ID}")
logger.info(f"Non-Ad-Block Group ID set to {NON_ADBLOCK_GROUP_ID}")

class APIs(Enum):
    """Enums for the specific Pi-hole API paths."""
    AUTH = '/api/auth/'
    CLIENTS = '/api/clients/'
    GROUPS = '/api/groups/'
