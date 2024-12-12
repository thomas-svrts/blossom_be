import logging
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .coordinator import BlossomDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Blossom select entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create the dropdown entity
    async_add_entities([BlossomModeSelect(coordinator, entry.entry_id)])

class BlossomModeSelect(SelectEntity):
    """Representation of a Blossom mode selector."""

    def __init__(self, coordinator: BlossomDataUpdateCoordinator, device_id : str):
        """Initialize the select entity."""
        self.coordinator = coordinator
        self.device_id  = device_id 
        self._name = "Charging Mode"
        
        """Initialize the Demo select entity."""
        self._attr_unique_id = f"mode_selector"
        self._attr_current_option = self.coordinator.data.get("set_points", {}).get("user_setting_mode", "solar")
        self._attr_options = ["solar", "cap"]

    @property
    def entity_category(self):
        return EntityCategory.CONFIG

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name="Charging Station",
            manufacturer="Blossom",
        )
        
    async def async_select_option(self, option: str):
        """Handle the option being changed."""
        if option in self._attr_options:
            cap_value = None
            if option == "cap":
                # Fetch the current value of the user_setting_cap_value sensor
                cap_value = self.coordinator.data.get("set_points", {}).get("user_setting_cap_value")
                if cap_value is None:
                    _LOGGER.error("Cannot switch to 'cap' mode: cap value is missing.")
                    return
                    
            _LOGGER.warning("Info: before update: option = %s and cap_value = %s", option, cap_value)
            # Call the API to update the mode
            await self.coordinator.update_mode(option, cap_value)
            self._attr_current_option = option
            self.coordinator.data["set_points"]["user_setting_mode"] = option
            self.async_write_ha_state()  # Notify Home Assistant of the change
