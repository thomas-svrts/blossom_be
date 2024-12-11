import logging
from .const import DOMAIN
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BlossomDataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
    EntityCategory,
    UnitOfElectricCurrent,
)

_LOGGER = logging.getLogger(__name__)

class BlossomSensor(SensorEntity):
    """Representation of a Demo sensor."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(
        self,
        unique_id: str,
        device_id: str | None,
        state: float | str | None,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass | None,
        unit_of_measurement: str | None,
        entity_category: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_native_value = state
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._attr_translation_key = unique_id
        self._attr_entity_category = entity_category

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="Charging Station",
            manufacturer="Blossom",
        )
            
class BlossomSensor_todelete(SensorEntity):
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
        
        return self.coordinator.data.get(self._api, {})data_section.get(self._key)

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
        BlossomSensor("peak_solar_capacity", device_id, self.coordinator.data.get("hems", {})data_section.get("peak_solar_capacity"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor("electricity_contract", device_id, self.coordinator.data.get("hems", {})data_section.get("electricity_contract"), 
                        None, None, None, EntityCategory.DIAGNOSTIC ),
        BlossomSensor("user_setting_mode", device_id, self.coordinator.data.get("set_points", {})data_section.get("user_setting_mode"), 
                        None, None, None, EntityCategory.CONFIG ),
        BlossomSensor("user_setting_cap_value", device_id, self.coordinator.data.get("set_points", {})data_section.get("user_setting_cap_value"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor("min_charge_rate", device_id, self.coordinator.data.get("set_points", {})data_section.get("min_charge_rate"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor("current_month_peak", device_id, self.coordinator.data.get("set_points", {})data_section.get("current_month_peak"), 
                        SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, UnitOfPower.WATT, None ),   
    ]
    
    async_add_entities(entities)
