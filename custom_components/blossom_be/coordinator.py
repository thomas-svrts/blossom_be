import logging
import aiohttp
from datetime import timedelta, datetime
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_REFRESH_TOKEN
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

# API endpoints
CURRENT_URL = "https://api.blossom.be/api/current"
SET_POINTS_URL = "https://api.blossom.be/api/hems/set-points"
HEMS_URL = "https://api.blossom.be/api/hems"
CONSUMPTION_URL = "https://api.blossom.be/api/hems/energy-consumption"
UPDATE_MODE_URL = "https://api.blossom.be/api/hems/set-points"
SESSION_URL = "https://api.blossom.be/api/hems/home-charging-session"
DEVICES_URL = "https://api.blossom.be/api/optimile/devices"
AUTH_URL = "https://blossom-production.eu.auth0.com/oauth/token"
CLIENT_ID = "RTofmsbiLPSlisRHtIFohGRPBcGgrIrs"

class BlossomDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch data from the Blossom API."""
    
    def __init__(self, hass: HomeAssistant, refresh_token: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(minutes=1),
        )
        _LOGGER.debug("Init coordinator")
        self.hass = hass
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expiry = None
        self.hems_last_fetched = None  # Initialize HEMS fetch timestamp
        self.hems_data = None          # Initialize HEMS data
        self.set_points_data = None    # Initialize set_points data
        self.consumption_data = None
        self.session_data = None
        self.devices_data = None
        self.member_id = None  # Will hold the memberId from /current

    async def async_refresh_access_token(self):
        """Refresh the access token only if it has expired."""
    
        # Check if we already have a valid access token
        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            _LOGGER.debug("Access token still valid.")
            return True
        
        if not self.refresh_token:
            _LOGGER.debug("No refresh token available, cannot refresh access token.")
            return None

        payload = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.token_expiry = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
                    # Subtract 5 minutes for buffer
                    self.token_expiry -= timedelta(minutes=5)
                    
                    # Store new refresh token for persistence after reboot.
                    store = Store(self.hass, version=1, key=f"{DOMAIN}_storage")
                    await store.async_save({CONF_REFRESH_TOKEN: self.refresh_token})
                    _LOGGER.debug("Refresh token stored to store.")
                else:
                    _LOGGER.error("Failed to refresh access token: %s", response.status)
                    raise Exception("Authentication error")
        return True

    async def _async_update_data(self):
        # Ensure the access token is valid
        if not await self.async_refresh_access_token():
            _LOGGER.error("Failed to refresh access token.")
            return None
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        now = datetime.utcnow()
        _LOGGER.debug("Coordinator: update_data triggered.")
        
        async with aiohttp.ClientSession() as session:
            try:
                # First, call /current to get the memberId
                async with session.get(CURRENT_URL, headers=headers) as current_response:
                    if current_response.status == 200:
                        current_data = await current_response.json()
                        members = current_data.get("members", [])
                        if members:
                            self.member_id = members[0].get("id")
                            _LOGGER.debug("Member ID retrieved: %s", self.member_id)
                        else:
                            _LOGGER.error("No members found in /current response.")
                            self.member_id = None
                    else:
                        _LOGGER.error("Failed to fetch /current endpoint: %s", current_response.status)
                        self.member_id = None

                # If we couldn't retrieve a member id, abort further API calls
                if not self.member_id:
                    _LOGGER.error("Member ID is not available. Skipping further API calls.")
                    return None

                # Prepare query parameter for subsequent calls
                params = {"memberId": self.member_id}

                # Fetch set_points
                async with session.get(SET_POINTS_URL, headers=headers, params=params) as response:
                    self.set_points_data = await response.json() if response.status == 200 else None
                    _LOGGER.debug("set_points_data refreshed successfully.")

                # Fetch consumption
                async with session.get(CONSUMPTION_URL, headers=headers, params=params) as consumption_response:
                    self.consumption_data = await consumption_response.json() if consumption_response.status == 200 else None
                    _LOGGER.debug("consumption_data refreshed successfully.")

                # Fetch session
                async with session.get(SESSION_URL, headers=headers, params=params) as session_response:
                    self.session_data = await session_response.json() if session_response.status == 200 else None
                    _LOGGER.debug("session_data refreshed successfully.")

                # Fetch HEMS and devices if cache expired
                if not self.hems_last_fetched or (now - self.hems_last_fetched).seconds > 3600:
                    async with session.get(HEMS_URL, headers=headers, params=params) as hems_response:
                        self.hems_data = await hems_response.json() if hems_response.status == 200 else None
                        self.hems_last_fetched = now
                        _LOGGER.debug("hems_data refreshed successfully.")

                    async with session.get(DEVICES_URL, headers=headers, params=params) as devices_response:
                        self.devices_data = await devices_response.json() if devices_response.status == 200 else None
                        _LOGGER.debug("devices_data refreshed successfully.")
                else:
                    _LOGGER.debug("hems/devices data not refreshed; cache is still valid. Last refresh %s seconds ago.",
                                  (now - self.hems_last_fetched).seconds)
    
                return {
                    "set_points": self.set_points_data,
                    "hems": self.hems_data,
                    "consumption": self.consumption_data,
                    "home-charging-session": self.session_data,
                    "devices": self.devices_data
                }
            except Exception as err:
                _LOGGER.error("Error fetching data from Blossom: %s", err)
                return None

    async def update_mode(self, mode: str, cap_value: int = None):
        """Update the mode of the Blossom charging station."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        params = {"memberId": self.member_id} if self.member_id else {}
        
        json_data = {"mode": mode}
        if cap_value:
            json_data["cap"] = cap_value
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(UPDATE_MODE_URL, json=json_data, headers=headers, params=params) as response:
                    if response.status in (200, 201):
                        _LOGGER.info("Successfully updated mode to %s.", mode)
                    else:
                        _LOGGER.error("Error updating mode: %s", response.status)
            except Exception as err:
                _LOGGER.error("Error sending mode update to Blossom: %s", err)
