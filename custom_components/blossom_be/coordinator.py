# coordinator.py
import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class BlossomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to fetch data from the Blossom API."""
    
    def __init__(self, hass: HomeAssistant, access_token: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="blossom_be_data",  # Unique name for the coordinator
            update_interval=timedelta(minutes=10),  # Update every 10 minutes
        )
        self._access_token = access_token
    
    async def _async_update_data(self):
        """Fetch the data from the Blossom API."""
        url = "https://api.blossom.be/api/hems/set-points"
        headers = {"Authorization": f"Bearer {self._access_token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()  # Return the API response as JSON
                else:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
