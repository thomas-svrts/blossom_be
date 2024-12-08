# config_flow.py
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

class BlossomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the Blossom integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user inputs the refresh token."""
        if user_input is not None:
            refresh_token = user_input.get(CONF_REFRESH_TOKEN)
            if refresh_token:              
                # Store refresh_token securely
                await self.hass.helpers.storage.async_save(
                    f"{DOMAIN}_refresh_token",
                    {"refresh_token": refresh_token},
                )
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
