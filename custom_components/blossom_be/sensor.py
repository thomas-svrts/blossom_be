import logging
from .const import DOMAIN
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
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

class BlossomSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Demo sensor."""

    def __init__(
        self,
        coordinator: BlossomDataUpdateCoordinator,
        unique_id: str,
        device_id: str | None,
        state: float | str | None,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass | None,
        unit_of_measurement: str | None,
        entity_category: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        _LOGGER.debug("Init Blosomsensor: %s.", unique_id)
        """Initialize the sensor."""
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        if unit_of_measurement == UnitOfEnergy.WATT_HOUR:
            self._attr_suggested_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_suggested_display_precision = 0
        self._attr_native_value = state
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._attr_name = unique_id
        self._attr_entity_category = entity_category

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="Charging Station",
            manufacturer="Blossom",
        )
    async def async_update(self):
        _LOGGER.debug("Update Blossomsensor")
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
        
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):   
    _LOGGER.debug("Setup_entry sensor platform.")
    # Access the coordinator stored in hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensors entities
    device_id = entry.entry_id
    entities = [
        BlossomSensor(coordinator, "peak_solar_capacity", device_id, coordinator.data.get("hems", {}).get("peak_solar_capacity"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "electricity_contract", device_id, coordinator.data.get("hems", {}).get("electricity_contract"), 
                        None, None, None, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "user_setting_cap_value", device_id, coordinator.data.get("set_points", {}).get("user_setting_cap_value"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "min_charge_rate", device_id, coordinator.data.get("set_points", {}).get("min_charge_rate"), 
                        SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "current_month_peak", device_id, coordinator.data.get("set_points", {}).get("current_month_peak"), 
                        SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, UnitOfPower.WATT, None ),   
        BlossomSensor(coordinator, "car_monthly_energy_consumption", device_id, coordinator.data.get("consumption", {}).get("carConsumptionWh"), 
                        SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, UnitOfEnergy.WATT_HOUR, None ),   
    ]
    
    async_add_entities(entities)
