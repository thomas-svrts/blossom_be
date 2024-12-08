# config_flow.py
import logging
from homeassistant import config_entries
import aiohttp
from .const import DOMAIN, CONF_REFRESH_TOKEN
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

class BlossomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the Blossom integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user inputs the refresh token."""
        if user_input is not None:
            refresh_token = user_input.get(CONF_REFRESH_TOKEN)
            if refresh_token:
                # Store the refresh token in secrets
                self.hass.helpers.secret.set(CONF_REFRESH_TOKEN, refresh_token)
                
                # Create the config entry with the refresh token
                return self.async_create_entry(
                    title="Blossom Integration", 
                    data={CONF_REFRESH_TOKEN: refresh_token}
                )
        
        # Prompt user for the refresh token
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_TOKEN): str,
            })
        )
