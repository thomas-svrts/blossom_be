import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import DOMAIN


_LOGGER = logging.getLogger(__name__)

# Replace with your actual API URL
SET_POINTS_URL = "https://api.blossom.be/api/hems/set-points"
UPDATE_MODE_URL = "https://api.blossom.be/api/hems/set-points"
AUTH_URL = "https://blossom-production.eu.auth0.com/oauth/token"
CLIENT_ID = "RTofmsbiLPSlisRHtIFohGRPBcGgrIrs"

class BlossomDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch data from the Blossom API."""
    
    def __init__(self, hass: HomeAssistant, refresh_token: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="{DOMAIN}_coordinator",
            update_interval=timedelta(minutes=10),  # Update every 10 minutes
        )
        self.hass = hass
        self.refresh_token = refresh_token
        self.access_token = None
        
    async def async_refresh_access_token(self):
        """Fetch a new access token using the refresh token."""
        payload = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_URL, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    self.refresh_token =  data["refresh_token"]
                    _LOGGER.debug("Access token refreshed successfully.")
                else:
                    _LOGGER.error("Failed to refresh access token: %s", response.status)
                    raise Exception("Authentication error")

    
    async def _async_update_data(self):
        """Fetch data from Blossom API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(SET_POINTS_URL, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data  # Return the JSON data
                    else:
                        _LOGGER.error(f"Error fetching data: {response.status}")
                        _LOGGER.error(f"Error fetching data: {headers}")
                        _LOGGER.error(f"Error fetching data: {response}")
                        return None
            except Exception as err:
                _LOGGER.error(f"Error fetching data from Blossom: {err}")
                return None


    async def update_mode(self, mode: str, cap_value: int = None):
        """Update the mode of the Blossom charging station."""
        headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
        
        json_data = {"mode": mode}
        if cap_value:
            json_data["cap"] = cap_value
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(UPDATE_MODE_URL, json=json_data, headers=headers) as response:
                    if response.status == 200:
                        _LOGGER.info(f"Successfully updated mode to {mode}.")
                    else:
                        _LOGGER.error(f"Error updating mode: {response.status}")
            except Exception as err:
                _LOGGER.error(f"Error sending mode update to Blossom: {err}")
