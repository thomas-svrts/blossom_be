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
    def __init__(self, coordinator, device_id, api, name, key):
        self.coordinator = coordinator
        self.device_id = device_id
        self._api = api
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
        _LOGGER.warning("creating native value for %s from api %s.", self._key, self._api)
        """Return the native value of the sensor."""
        if not self.coordinator.data:
            _LOGGER.warning("Coordinator data is None. Returning None for %s.", self._key)
            return None

        # Fetch either "hems" or "setpoints" data based on the key
        data_section = self.coordinator.data.get(self._api)
        if not data_section:
            _LOGGER.warning("Data section '%s' is None. Returning None for %s.", self._api, self._key)
            return None    
        
        return data_section.get(self._key)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name="Blossom Device",
            manufacturer="Blossom",
            model="Charging station",
        )
        
    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
        
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):   
    # Access the coordinator stored in hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensors entities
    device_id = entry.entry_id
    entities = [
        BlossomSensor(coordinator, device_id, "hems", "Peak Solar Capacity", "peak_solar_capacity"),
        BlossomSensor(coordinator, device_id, "hems", "Electricity Export Price", "elek_export_price"),
        BlossomSensor(coordinator, device_id, "hems", "Electricity Import Price", "elek_import_price"),
        BlossomSensor(coordinator, device_id, "hems", "Electricity Contract", "electricity_contract"),
        BlossomSensor(coordinator, device_id, "set_points", "User Setting Mode", "user_setting_mode"),
        BlossomSensor(coordinator, device_id, "set_points", "User Setting Cap Value", "user_setting_cap_value"),
        BlossomSensor(coordinator, device_id, "set_points", "Min Charge Rate", "min_charge_rate"),
        BlossomSensor(coordinator, device_id, "set_points", "Max Charge Rate", "max_charge_rate"),
        BlossomSensor(coordinator, device_id, "set_points", "Current Month Peak", "current_month_peak"),
    ]
    
    async_add_entities(entities)
