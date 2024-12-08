import logging
import aiohttp
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# Replace with your actual API URL
SET_POINTS_URL = "https://api.blossom.be/api/hems/set-points"
UPDATE_MODE_URL = "https://api.blossom.be/api/hems/set-points"

class BlossomDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch data from the Blossom API."""
    
    def __init__(self, hass: HomeAssistant, access_token: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="blossom_be_data",
            update_interval=timedelta(minutes=10),  # Update every 10 minutes
        )
        self._access_token = access_token
    
    async def _async_update_data(self):
        """Fetch data from Blossom API."""
        headers = {"Authorization": f"Bearer {self._access_token}"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(SET_POINTS_URL, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data  # Return the JSON data
                    else:
                        _LOGGER.error(f"Error fetching data: {response.status}")
                        return None
            except Exception as err:
                _LOGGER.error(f"Error fetching data from Blossom: {err}")
                return None

    async def update_mode(self, mode: str, cap_value: int = None):
        """Update the mode of the Blossom charging station."""
        headers = {"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"}
        
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
