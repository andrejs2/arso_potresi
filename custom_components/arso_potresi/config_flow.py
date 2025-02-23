import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

class ArsoPotresiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow za ARSO Potresi integracijo."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Obdelaj vnos uporabnika."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="ARSO Potresi", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
        })
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
