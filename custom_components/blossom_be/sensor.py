import logging
from datetime import datetime
from typing import Any
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
        parameter: str | None,
        device_class: SensorDeviceClass,
        state_class: SensorStateClass | None,
        unit_of_measurement: str | None,
        entity_category: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        _LOGGER.debug("Init Blosomsensor: %s, parameter: %s", unique_id, parameter)
        """Initialize the sensor."""
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        if unit_of_measurement == UnitOfEnergy.WATT_HOUR:
            self._attr_suggested_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_suggested_display_precision = 0
        if unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR:
            self._attr_suggested_display_precision = 2
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._attr_name = unique_id
        self._attr_entity_category = entity_category
        self._parameter= parameter
        self._attr_translation_key = unique_id
        self._attr_has_entity_name = True

        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="Charging Station",
            manufacturer="Blossom",
        )
        
    @property
    def native_value(self) -> str | datetime | None:
        """Return the current state."""
        # Get the full data structure from the coordinator
        data = self.coordinator.data
    
        # Split the _parameter by dots (e.g., "home-charging-session.session.status")
        keys = self._parameter.split(".")

        previous_key = None  # Initialize to track the parent key
        # Traverse the data using the keys
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list):
                key = int(key)  # Convert key to integer for list indexing
                data = data[key]
            else:
                # If session is missing, return None or handle it
                if previous_key == "session" and data is None:
                    _LOGGER.debug("No session data; station status is '%s'.", 
                                  self.coordinator.data.get("home-charging-session", {}).get("status"))
                    if self._parameter == "home-charging-session.session.status":
                        return "NOT_ACTIVE"
                    if self._parameter == "home-charging-session.session.kWh":
                        return self._last_known_consumption if hasattr(self, "_last_known_consumption") else 0                   
                # If the key path is invalid or not a dict, return None
                _LOGGER.warning("Invalid key path: %s", self._parameter)
                return None
                
            # Update previous_key for the next iteration
            previous_key = key
    
        
        # If this is a timestamp field, convert to datetime
        if self._parameter == "home-charging-session.session.time_started_session":
            return datetime.fromisoformat(data)
    
        # If this is the session status field, handle splitting
        if self._parameter == "home-charging-session.status" and isinstance(data, str):
            # Store the full value for attributes
            self._full_status = data
    
            # Split the value and return only the status
            parts = data.split("; info: ")
            if len(parts) > 1:
                return parts[0].strip().lower()  # Return just the status

        if self._parameter == "home-charging-session.session.kWh":
            # Sessie actief? behoud laatste waarde
            self._last_known_consumption = data  # Bewaar de huidige waarde
    
        # Default return: raw data
        return data
        
    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        attributes = {}
    
        # Split and add status and info if _full_status is existing
        if hasattr(self, "_full_status") and isinstance(self._full_status, str):
            parts = self._full_status.split("; info: ")
            if len(parts) > 1:
                attributes["status"] = parts[0].strip()
                attributes["info"] = parts[1].strip()
                
        return attributes
      
        
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):   
    _LOGGER.debug("Setup_entry sensor platform.")
    # Access the coordinator stored in hass.data
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create sensors entities
    device_id = entry.entry_id
    entities = [
        BlossomSensor(coordinator, "peak_solar_capacity", device_id,    "hems.peak_solar_capacity",     SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "electricity_contract", device_id,   "hems.electricity_contract",    None, None, None, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "user_setting_cap_value", device_id, "set_points.user_setting_cap_value",  SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "min_charge_rate", device_id,        "set_points.min_charge_rate",         SensorDeviceClass.POWER, None, UnitOfPower.WATT, EntityCategory.DIAGNOSTIC ),
        BlossomSensor(coordinator, "current_month_peak", device_id,     "set_points.current_month_peak",      SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, UnitOfPower.WATT, None ),   
        BlossomSensor(coordinator, "monthly_energy_consumption", device_id, "consumption.carConsumptionWh",    SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, UnitOfEnergy.WATT_HOUR, None ),   
        BlossomSensor(coordinator, "last_session_status", device_id,         "home-charging-session.session.status",    None, None, None, None ),   
        BlossomSensor(coordinator, "last_session_consumption", device_id,    "home-charging-session.session.kWh",    SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, UnitOfEnergy.KILO_WATT_HOUR, None ),   
        BlossomSensor(coordinator, "last_session_start", device_id,          "home-charging-session.session.time_started_session",    SensorDeviceClass.TIMESTAMP, None, None, None ),
        BlossomSensor(coordinator, "home_charging_status", device_id,   "home-charging-session.status",    None, None, None, None ),   
        
        BlossomSensor(coordinator, "energy_component_price", device_id,  "devices.0.device.charging_points.0.pricing_policy.energy_components.0.price",    SensorDeviceClass.MONETARY, None, "EUR", None ),   
    ]
    
    async_add_entities(entities)
