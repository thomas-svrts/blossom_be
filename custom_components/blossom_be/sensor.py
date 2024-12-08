# sensor.py
import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    refresh_token = config_entry.data.get(CONF_REFRESH_TOKEN)
    
    # Fetch a new access token using the refresh token
    access_token = await get_access_token(hass, refresh_token)
    if access_token is None:
        _LOGGER.error("Failed to obtain access token")
        return
    
    coordinator = BlossomDataUpdateCoordinator(hass, access_token)
    await coordinator.async_refresh()

    async_add_entities([BlossomSensor(coordinator)], update_before_add=True)


async def get_access_token(hass, refresh_token):
    """Get a new access token using the refresh token."""
    token_url = "https://blossom-production.eu.auth0.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": "RTofmsbiLPSlisRHtIFohGRPBcGgrIrs",
        "refresh_token": refresh_token
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=data) as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json.get("access_token")
            else:
                _LOGGER.error("Failed to get access token: %s", response.status)
                return None


class BlossomDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to fetch data from the REST API."""

    def __init__(self, hass, access_token):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="blossom_be_data",
            update_interval=timedelta(minutes=10),
        )
        self._access_token = access_token

    async def _async_update_data(self):
        """Fetch data from the REST API."""
        url = "https://example.com/api/data"  # Replace with actual API URL

        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                return await response.json()


class BlossomSensor(Entity):
    """Representation of a Blossom sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = "Blossom Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("sensor_value")  # Replace with actual data key

    async def async_update(self):
        """Update the sensor state."""
        await self.coordinator.async_request_refresh()
