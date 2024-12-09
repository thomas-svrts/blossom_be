import logging
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
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

    def __init__(self, coordinator: BlossomDataUpdateCoordinator, entry_id: str):
        """Initialize the select entity."""
        self.coordinator = coordinator
        self.entry_id = entry_id
        self._attr_name = "Blossom Mode"
        self._attr_options = ["solar", "cap"]
        self._attr_current_option = "solar"  # Default mode
        self._attr_entity_category = EntityCategory.CONFIG
        
    @property
    def device_info(self):
        """Return device information to link the entity to the device."""
        return {
            "identifiers": {(DOMAIN, self.entry_id)},  # Link the entity to the device
            "name": "Blossom Device",
            "manufacturer": "Blossom",
            "model": "Charging station",
        }
    
    async def async_select_option(self, option: str):
        """Handle the option being changed."""
        if option in self._attr_options:
            # Call the API to update the mode
            await self.coordinator.update_mode(option)
            self._attr_current_option = option
            self.async_write_ha_state()  # Notify Home Assistant of the change
