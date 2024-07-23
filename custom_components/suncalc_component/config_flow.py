import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class SunCalcConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SunCalc."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="SunCalc", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LATITUDE): cv.latitude,
                vol.Required(CONF_LONGITUDE): cv.longitude,
            }),
            errors={},
            description_placeholders={
                "latitude": "Enter the latitude for your location",
                "longitude": "Enter the longitude for your location"
            }
        )
