import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_REFRESH_TOKEN
from datetime import datetime, timedelta
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)

# Replace with your actual API URL
SET_POINTS_URL = "https://api.blossom.be/api/hems/set-points"
HEMS_URL = "https://api.blossom.be/api/hems"
CONSUMPTION_URL = "https://api.blossom.be/api/energy-consumption"
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
        self.token_expiry = None
        self.hems_last_fetched = None  # Initialize HEMS fetch timestamp
        self.hems_data = None          # Initialize HEMS data
        self.set_points_data = None    # Initialize set_points data
        self.consumption_data = None
        
    async def async_refresh_access_token(self):
        """Refresh the access token only if it has expired."""
    
        # Check if we already have a valid access token
        if self.access_token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            # Token is still valid, no need to refresh
            return True
        
        # If we don't have a valid token or the token has expired, refresh it
        if not self.refresh_token:
            _LOGGER.error("No refresh token available, cannot refresh access token.")
            return None

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
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    self.token_expiry = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))  # Set expiration time
                    # Subtract 5 minutes from the expiration time for a buffer
                    self.token_expiry -= timedelta(minutes=5)
                    
                    # store new refresh token in store for persisting after reboot.
                    store = Store(self.hass, version=1, key=f"{DOMAIN}_storage")
                    await store.async_save({CONF_REFRESH_TOKEN: self.refresh_token})  
                else:
                    _LOGGER.error("Failed to refresh access token: %s", response.status)
                    raise Exception("Authentication error")
        return True

    
    async def _async_update_data(self):
        # Ensure the access token is valid and not expired
        if not await self.async_refresh_access_token():
            _LOGGER.error("Failed to refresh access token.")
            return None
        
        """Fetch data from Blossom API."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        now = datetime.utcnow()
        
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch set_points
                async with session.get(SET_POINTS_URL, headers=headers) as response:
                    self.set_points_data = await response.json() if response.status == 200 else None
                    _LOGGER.warning("Info: set_points_data refreshed successfully.")
                    
                # Fetch consumption
                async with session.get(CONSUMPTION_URL, headers=headers) as response:
                    self.consumption_data = await response.json() if response.status == 200 else None
                    _LOGGER.warning("Info: consumption_data refreshed successfully.")
    
                # Fetch HEMS data if cache expired
                if not self.hems_last_fetched or (now - self.hems_last_fetched).seconds > 3600:
                    async with session.get(HEMS_URL, headers=headers) as hems_response:
                        self.hems_data = await hems_response.json() if hems_response.status == 200 else None
                        self.hems_last_fetched = now
                        _LOGGER.warning("Info: hems refreshed successfully")
                else:
                    _LOGGER.warning("Info: hems not refreshed, still up to date. Last refresh %s seconds ago.", (now - self.hems_last_fetched).seconds)
    
                return {"set_points": self.set_points_data, "hems": self.hems_data, "consumption": self.consumption }
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
                    if response.status in (200, 201):
                        _LOGGER.info(f"Successfully updated mode to {mode}.")
                    else:
                        _LOGGER.error(f"Error updating mode: {response.status}")
            except Exception as err:
                _LOGGER.error(f"Error sending mode update to Blossom: {err}")
