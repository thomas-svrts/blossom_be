# config_flow.py
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.storage import Store

from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

class BlossomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the Blossom integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user inputs the refresh token."""
        errors = {}
        store = Store(self.hass, version=1, key=f"{DOMAIN}_storage")
        if user_input is not None:
            refresh_token = user_input.get(CONF_REFRESH_TOKEN)
    
            # Validate the refresh token by attempting to fetch an access token
            is_valid, details = await self._validate_refresh_token(refresh_token)
    
            if is_valid:
                # Save the refresh token securely
                await store.async_save({CONF_REFRESH_TOKEN: refresh_token})
    
                # Create the config entry
                return self.async_create_entry(
                    title="Blossom Integration",
                    data={CONF_REFRESH_TOKEN: refresh_token,
                          "server_details": details},  # Optionally store server details
                )
            else:
                # Use detailed error message from the server response
                errors["base"] = details.get("error", "unknown_error")
  
        # Prompt user for the refresh token
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_TOKEN): str,
            }),
            errors=errors
        )

    async def _validate_refresh_token(self, refresh_token):
        """Validate the provided refresh token by fetching an access token."""
        import aiohttp
    
        url = "https://blossom-production.eu.auth0.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": "RTofmsbiLPSlisRHtIFohGRPBcGgrIrs",
            "refresh_token": refresh_token,
        }
    
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as resp:
                    response_data = await resp.json()
    
                    if resp.status == 200:
                        return True, response_data  # Access token retrieved successfully
                    else:
                        # Return failure and the server's error response                  
                        _LOGGER.error(
                            "Failed to validate refresh token. Status: %s, Response: %s",
                            resp.status,
                            response_data
                        )
                        return False, response_data
            except aiohttp.ClientError as e:
                # Handle network errors
                return False, {"error": "network_error", "details": str(e)}
    
        # Generic failure fallback
        return False, {"error": "unknown_error"}
