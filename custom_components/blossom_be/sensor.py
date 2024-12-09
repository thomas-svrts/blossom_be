import logging
from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BlossomDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry


_LOGGER = logging.getLogger(__name__)

class BlossomSensor(SensorEntity):
    def __init__(self, coordinator, device_id, name, key):
        self.coordinator = coordinator
        self.device_id = device_id
        self._name = name
        self._key = key

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"{self.device_id}_{self._key}"

    @property
    def native_value(self):
        return self.coordinator.data.get("hems" if "hems" in self._key else "setpoints").get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name="Blossom Device",
            manufacturer="Blossom",
            model="Energy Device",
        )


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
    
    # Create sensors entities
    device_id = entry.entry_id
    entities = [
        BlossomSensor(coordinator, device_id, "Peak Solar Capacity", "peak_solar_capacity"),
        BlossomSensor(coordinator, device_id, "Electricity Export Price", "elek_export_price"),
        BlossomSensor(coordinator, device_id, "Electricity Import Price", "elek_import_price"),
        BlossomSensor(coordinator, device_id, "Electricity Contract", "electricity_contract"),
        BlossomSensor(coordinator, device_id, "User Setting Mode", "user_setting_mode"),
        BlossomSensor(coordinator, device_id, "User Setting Cap Value", "user_setting_cap_value"),
        BlossomSensor(coordinator, device_id, "Min Charge Rate", "min_charge_rate"),
        BlossomSensor(coordinator, device_id, "Max Charge Rate", "max_charge_rate"),
        BlossomSensor(coordinator, device_id, "Current Month Peak", "current_month_peak"),
    ]
    
    async_add_entities(entities)


    # Example usage of mode update: You can use this in automations or service calls
    # coordinator.update_mode("solar")
