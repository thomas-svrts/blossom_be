import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BlossomDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)

class BlossomChargingStation(SensorEntity):
    """Representation of a Blossom charging station."""

    def __init__(self, coordinator, unique_id: str, name: str):
        """Initialize the charging station sensor."""
        self.coordinator = coordinator
        self._unique_id = unique_id
        self._name = name
        self._attr_name = name
        self._attr_unique_id = unique_id

    @property
    def state(self):
        """Return the state of the charging station (e.g., mode)."""
        data = self.coordinator.data
        if data:
            return data.get("user_setting_mode")
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data
        if data:
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
        return {}

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

    async def set_mode(self, mode: str, cap_value: int = None):
        """Change the mode of the charging station."""
        await self.coordinator.update_mode(mode, cap_value)
        await self.coordinator.async_request_refresh()

# Example Home Assistant Integration Setup
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):   
    # Access the coordinator stored in hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Add the Blossom charging station sensor
    async_add_entities([BlossomChargingStation(coordinator, "blossom_charging_station", "Blossom Charging Station")])

    # Example usage of mode update: You can use this in automations or service calls
    # coordinator.update_mode("solar")
