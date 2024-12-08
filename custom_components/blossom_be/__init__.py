# __init__.py
from homeassistant import config_entries
from .const import DOMAIN
from .config_flow import BlossomConfigFlow
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import BlossomDataUpdateCoordinator

async def async_setup(hass, config):
    """Set up the Blossom integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Blossom from a config entry."""
    
    # Get stored refresh token (if any) from secret storage or elsewhere
    stored_data = await hass.helpers.storage.async_load(f"{DOMAIN}_refresh_token")
    refresh_token = stored_data.get("refresh_token")
    
    # Create a coordinator to manage data fetching
    coordinator = BlossomDataUpdateCoordinator(hass, refresh_token)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Perform the first data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Set up the platform (sensor)
    await hass.config_entries.async_setup_platforms(entry, ["sensor"])

    return True
