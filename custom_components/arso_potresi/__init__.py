from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DEFAULT_HISTORY_DAYS

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Nastavi integracijo preko config entryja."""
    from .sensor import ArsoDataCoordinator

    hass.data.setdefault(DOMAIN, {})

    options = config_entry.options or config_entry.data
    scan_interval = options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    history_days = options.get("history_days", DEFAULT_HISTORY_DAYS)

    coordinator = ArsoDataCoordinator(hass, scan_interval, history_days)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Odstrani integracijo."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Ponovno naloži integracijo."""
    await hass.config_entries.async_reload(config_entry.entry_id)
