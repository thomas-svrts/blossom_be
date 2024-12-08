# sensor.py
import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the charging station and sensors."""
    refresh_token = config_entry.data.get(CONF_REFRESH_TOKEN)
    
    # Fetch a new access token using the refresh token
    access_token = await get_access_token(hass, refresh_token)
    if access_token is None:
        _LOGGER.error("Failed to obtain access token")
        return
    
    coordinator = BlossomDataUpdateCoordinator(hass, access_token)
    await coordinator.async_refresh()

    async_add_entities([BlossomChargingStation(coordinator)], update_before_add=True)


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
    """Class to fetch data from the Blossom API."""

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
        """Fetch data from the Blossom API."""
        url = "https://api.blossom.be/api/hems/set-points"
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                return await response.json()


class BlossomChargingStation(Entity):
    """Representation of a Blossom Charging Station."""

    def __init__(self, coordinator):
        """Initialize the charging station."""
        self.coordinator = coordinator
        self._attr_name = "Blossom Charging Station"
        self._attr_unique_id = "blossom_charging_station"

    @property
    def state(self):
        """Return the state of the charging station (e.g., mode)."""
        return self.coordinator.data.get("user_setting_mode")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        return {
            "charger_id": data.get("charger_id"),
            "charge_need_km": data.get("charge_need_km"),
            "charge_end_date": data.get("charge_end_date"),
            "online": data.get("online"),
            "min_charge_rate": data.get("min_charge_rate"),
            "max_charge_rate": data.get("max_charge_rate"),
            "km_hour_charge": data.get("km_hour_charge"),
            "recommended_minute_charge_km": data.get("recommended_minute_charge_km"),
            "start_session_timestamp": data.get("start_session_timestamp")
        }

    async def async_update(self):
        """Update the state of the charging station."""
        await self.coordinator.async_request_refresh()


class BlossomChargingStationButton(ButtonEntity):
    """Button to change the mode of the charging station."""

    def __init__(self, coordinator, mode, cap_value=None):
        """Initialize the button."""
        self.coordinator = coordinator
        self.mode = mode
        self.cap_value = cap_value

    @property
    def name(self):
        """Return the name of the button."""
        return f"Set mode to {self.mode}"

    async def async_press(self):
        """Handle button press to change mode."""
        await self.set_mode()

    async def set_mode(self):
        """Send the mode change request."""
        url = "https://api.blossom.be/api/hems/set-points"
        headers = {
            "Authorization": f"Bearer {self.coordinator._access_token}",
            "Content-Type": "application/json"
        }

        if self.mode == "solar":
            data = {"mode": "solar"}
        elif self.mode == "cap" and self.cap_value:
            data = {"mode": "cap", "cap": self.cap_value}
        else:
            _LOGGER.error("Invalid mode or cap value")
            return

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    _LOGGER.info(f"Successfully updated mode to {self.mode}")
                else:
                    _LOGGER.error(f"Failed to update mode: {response.status}")
