import logging
from datetime import timedelta, datetime
import aiohttp
import async_timeout
import pytz

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.util.dt import parse_datetime
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEFAULT_API_URL, DEFAULT_SCAN_INTERVAL, DEFAULT_HISTORY_DAYS

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Vir: ARSO Potresi - Agencija RS za okolje"
DEVICE_NAME = "ARSO Potresi"

def format_datetime(dt_obj):
    """Oblikuj datum v obliki: '20. 2. 2025 ob 23.11'."""
    if dt_obj is None:
        return "Neznano"
    return f"{dt_obj.day}. {dt_obj.month}. {dt_obj.year} ob {dt_obj.hour:02d}.{dt_obj.minute:02d}"

def format_decimal(value):
    """Oblikuj decimalno vrednost in zamenjaj piko z vejico."""
    try:
        return f"{float(value):.1f}".replace(".", ",")
    except (ValueError, TypeError):
        return "Neznano"

async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Nastavi ARSO Potresi senzor iz config entryja."""
    options = config_entry.options or config_entry.data
    scan_interval = options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
    history_days = options.get("history_days", DEFAULT_HISTORY_DAYS)
    async_add_entities([ArsoPotresiSensor(scan_interval, history_days)], True)

class ArsoPotresiSensor(Entity):
    """Senzor, ki prikazuje zadnji potres z oblikovanimi podatki."""

    def __init__(self, scan_interval, history_days):
        self._api_url = DEFAULT_API_URL
        self._scan_interval = timedelta(minutes=scan_interval)
        self._history_days = history_days
        self._state = None
        self._attributes = {}
        self._name = "ARSO Potresi"
        self._icon = "mdi:pulse"
        self._unique_id = "arso_potresi_sensor"

    @property
    def unique_id(self):
        """Vrne edinstven ID entitete."""
        return self._unique_id

    @property
    def name(self):
        """Ime entitete."""
        return self._name

    @property
    def state(self):
        """Vrne trenutno stanje – lokalno lokacijo zadnjega potresa."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Dodatni atributi s podatki o potresu."""
        return self._attributes

    @property
    def device_info(self):
        """Informacije o napravi."""
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": DEVICE_NAME,
            "manufacturer": "ARSO",
            "model": "Potresi"
        }

    async def async_update(self):
        """Osveži podatke s klicanjem ARSO Potresi API-ja."""
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    async with session.get(self._api_url) as response:
                        if response.status != 200:
                            _LOGGER.error("Napaka pri pridobivanju podatkov: %s", response.status)
                            return
                        data = await response.json()
                        if not data:
                            _LOGGER.warning("Prejeto ni bilo podatkov")
                            return

                        now = datetime.now(pytz.utc)
                        time_limit = now - timedelta(days=self._history_days)
                        
                        filtered_earthquakes = [e for e in data if parse_datetime(e.get("TIME")).astimezone(pytz.utc) >= time_limit]
                        
                        if not filtered_earthquakes:
                            _LOGGER.warning("Ni potresov v izbranem časovnem obdobju.")
                            self._state = "Ni potresov"
                            self._attributes = {}
                            return

                        latest = filtered_earthquakes[0]

                        dt_local = parse_datetime(latest.get("TIME"))
                        try:
                            dt_utc = pytz.UTC.localize(datetime.strptime(latest.get("TIME_ORIG"), "%Y-%m-%d %H:%M:%S"))
                        except Exception:
                            dt_utc = None

                        lat_str = f"{latest.get('LAT')}".replace(".", ",") if latest.get("LAT") is not None else "Neznano"
                        lon_str = f"{latest.get('LON')}".replace(".", ",") if latest.get("LON") is not None else "Neznano"
                        lat_lon = f"{lat_str} / {lon_str}"

                        depth = f"{latest.get('DEPTH')} km" if latest.get("DEPTH") is not None else "Neznano"
                        mag = format_decimal(latest.get("MAG1"))
                        intensity = latest.get("INTENZITETA") if latest.get("INTENZITETA") is not None else "-"
                        verified = "DA" if latest.get("REVISION") == 1 else "NE"

                        self._state = latest.get("GEOLOC", "Neznano")
                        self._attributes = {
                            "Lokalni čas potresa": format_datetime(dt_local),
                            "Čas potresa v UTC": format_datetime(dt_utc),
                            "Nadžarišče": latest.get("GEOLOC", "Neznano"),
                            "Zemljepisna širina/dolžina": lat_lon,
                            "Globina": depth,
                            "Magnituda": mag,
                            "Največja intenziteta EMS-98": intensity,
                            "Preverjeno s strani seizmologa": verified,
                            ATTR_ATTRIBUTION: ATTRIBUTION,
                        }
                        
                        history = []
                        for earthquake in filtered_earthquakes:
                            dt_local_hist = parse_datetime(earthquake.get("TIME"))
                            try:
                                dt_utc_hist = pytz.UTC.localize(datetime.strptime(earthquake.get("TIME_ORIG"), "%Y-%m-%d %H:%M:%S"))
                            except Exception:
                                dt_utc_hist = None

                            lat_str_hist = f"{earthquake.get('LAT')}".replace(".", ",") if earthquake.get("LAT") is not None else "Neznano"
                            lon_str_hist = f"{earthquake.get('LON')}".replace(".", ",") if earthquake.get("LON") is not None else "Neznano"
                            lat_lon_hist = f"{lat_str_hist} / {lon_str_hist}"

                            depth_hist = f"{earthquake.get('DEPTH')} km" if earthquake.get("DEPTH") is not None else "Neznano"
                            mag_hist = format_decimal(earthquake.get("MAG1"))
                            intensity_hist = earthquake.get("INTENZITETA") if earthquake.get("INTENZITETA") is not None else "-"
                            verified_hist = "DA" if earthquake.get("REVISION") == 1 else "NE"
                            
                            earthquake_data = {
                                "Lokalni čas potresa": format_datetime(dt_local_hist),
                                "Čas potresa v UTC": format_datetime(dt_utc_hist),
                                "Nadžarišče": earthquake.get("GEOLOC", "Neznano"),
                                "Zemljepisna širina/dolžina": lat_lon_hist,
                                "Globina": depth_hist,
                                "Magnituda": mag_hist,
                                "Največja intenziteta EMS-98": intensity_hist,
                                "Preverjeno s strani seizmologa": verified_hist,
                            }
                            history.append(earthquake_data)

                        self._attributes["Zgodovina potresov"] = history

        except Exception as e:
            _LOGGER.error("Prišlo je do izjeme pri async_update: %s", e)
