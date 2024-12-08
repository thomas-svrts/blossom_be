from homeassistant import config_entries
import logging
import aiohttp
import asyncio
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

class Auth0ConfigFlow(config_entries.ConfigFlow, domain="blossom_be"):
    """Handle a config flow for your integration."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step where the user inputs the refresh token."""
        if user_input is not None:
            # Get the refresh token from the user input
            refresh_token = user_input.get(CONF_REFRESH_TOKEN)
            
            # Store the refresh token in the secrets file
            self._store_refresh_token(refresh_token)

            # Create the config entry with the refresh token
            return self.async_create_entry(
                title="Blossom Auth0 Integration", 
                data={CONF_REFRESH_TOKEN: refresh_token}
            )

        # Ask for the refresh token if not provided
        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema({
                vol.Required(CONF_REFRESH_TOKEN): str,
            })
        )

    def _store_refresh_token(self, refresh_token):
        """Store the refresh token securely in the secrets.yaml."""
        # Save the refresh token to the secrets file (this is how HA stores secrets securely)
        secrets = self.hass.config.items
        secrets[CONF_REFRESH_TOKEN] = refresh_token
        self.hass.config.save(secrets)

    async def async_get_access_token(self):
        """Use the stored refresh token to get a new access token."""
        # Retrieve the refresh token from the secrets storage
        refresh_token = self.hass.config.get(CONF_REFRESH_TOKEN)
        if not refresh_token:
            _LOGGER.error("No refresh token available")
            return None
        
        # Exchange the refresh token for an access token
        token_url = "https://blossom-production.eu.auth0.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": "RTofmsbiLPSlisRHtIFohGRPBcGgrIrs",
            "client_secret": "YOUR_CLIENT_SECRET",  # Replace with the actual client secret
            "refresh_token": refresh_token
        }

        # Make the HTTP request to get the new access token
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                response_json = await response.json()
                if response.status == 200:
                    return response_json.get("access_token")
                else:
                    _LOGGER.error("Failed to retrieve access token: %s", response_json)
                    return None
