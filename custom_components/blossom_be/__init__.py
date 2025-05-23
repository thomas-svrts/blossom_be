# __init__.py
import logging
import asyncio
from .const import DOMAIN, CONF_REFRESH_TOKEN
from .coordinator import BlossomDataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "select"]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    _LOGGER.debug("Setup entry component.")
    """Set up the integration from a config entry."""
    if DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]:
        return True

    # Load stored data
    store = Store(hass, version=1, key=f"{DOMAIN}_storage")
    stored_data = await store.async_load()

    # Check if the refresh token is available in storage
    refresh_token = stored_data.get(CONF_REFRESH_TOKEN) if stored_data else None

    # Perform the first data fetch
    coordinator = BlossomDataUpdateCoordinator(hass, refresh_token)
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator    
    await coordinator.async_config_entry_first_refresh()

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unload entry component.")
    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    unload_ok = True
    for platform in PLATFORMS:
        if not await hass.config_entries.async_forward_entry_unload(config_entry, platform):
            unload_ok = False
            break

    return unload_ok
