import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.config_entries import OptionsFlowWithConfigEntry

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DEFAULT_HISTORY_DAYS

class ArsoPotresiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow za ARSO Potresi integracijo."""
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Vrne opcije toka za to integracijo."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Obdelaj vnos uporabnika."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="ARSO Potresi", data=user_input)

        data_schema = vol.Schema({
            vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
            vol.Optional("history_days", default=DEFAULT_HISTORY_DAYS): int,
        })
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

class OptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Tok možnosti za ARSO Potresi integracijo."""

    async def async_step_init(self, user_input=None):
        """Upravljanje možnosti."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        options = self.config_entry.options or self.config_entry.data

        options_schema = vol.Schema({
            vol.Optional(
                "scan_interval", 
                default=options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
            ): int,
            vol.Optional(
                "history_days", 
                default=options.get("history_days", DEFAULT_HISTORY_DAYS)
            ): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            description_placeholders={
                "scan_interval": options.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                "history_days": options.get("history_days", DEFAULT_HISTORY_DAYS),
            },
        )

