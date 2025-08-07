from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "arso_potresi"

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Nastavi integracijo preko config entryja."""
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Odstrani integracijo."""
    return await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Ponovno naloži integracijo, ko se spremenijo nastavitve."""
    await hass.config_entries.async_reload(config_entry.entry_id)
