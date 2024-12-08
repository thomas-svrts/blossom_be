# __init__.py
from .const import DOMAIN
from .coordinator import BlossomDataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store

async def async_setup(hass, config):
    """Set up the Blossom integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Blossom from a config entry."""
    # Load stored data
    store = Store(hass, version=1, key=f"{DOMAIN}_storage")
    stored_data = await store.async_load()

    # Check if the refresh token is available in storage
    refresh_token = stored_data.get("refresh_token") if stored_data else None
    
    # Create a coordinator to manage data fetching
    coordinator = BlossomDataUpdateCoordinator(hass, refresh_token)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Perform the first data fetch
    await coordinator.async_config_entry_first_refresh()

    # Forward setup for the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
