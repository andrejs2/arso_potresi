from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Nastavi integracijo preko config entryja."""
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Odstrani integracijo."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Ponovno naloži integracijo."""
    await hass.config_entries.async_reload(config_entry.entry_id)
