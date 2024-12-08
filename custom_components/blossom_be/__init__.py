# __init__.py
from homeassistant import config_entries
from .const import DOMAIN
from .config_flow import BlossomConfigFlow

async def async_setup(hass, config):
    """Set up the Blossom integration."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Blossom from a config entry."""
    return await async_setup_entry(hass, entry)
