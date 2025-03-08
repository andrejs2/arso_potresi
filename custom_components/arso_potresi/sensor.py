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

from .const import DOMAIN, DEFAULT_API_URL

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
    scan_interval = config_entry.data.get("scan_interval", 5)
    async_add_entities([ArsoPotresiSensor(scan_interval)], True)

class ArsoPotresiSensor(Entity):
    """Senzor, ki prikazuje zadnji potres z oblikovanimi podatki."""

    def __init__(self, scan_interval):
        self._api_url = DEFAULT_API_URL  # API URL je hardcoded
        self._scan_interval = timedelta(minutes=scan_interval)
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

                        # Izberemo prvi element, predpostavljamo, da je najnovejši potres.
                        latest = data[0]

                        # Parse lokalnega časa iz TIME (npr. "2025-02-20T23:11:16+0100")
                        dt_local = parse_datetime(latest.get("TIME"))
                        # Parse UTC časa iz TIME_ORIG (npr. "2025-02-20 22:11:16") in označimo UTC
                        try:
                            dt_utc = pytz.UTC.localize(datetime.strptime(latest.get("TIME_ORIG"), "%Y-%m-%d %H:%M:%S"))
                        except Exception:
                            dt_utc = None

                        # Formatiramo geografske koordinate, pretvorimo piko v vejico
                        lat_str = f"{latest.get('LAT')}".replace(".", ",") if latest.get("LAT") is not None else "Neznano"
                        lon_str = f"{latest.get('LON')}".replace(".", ",") if latest.get("LON") is not None else "Neznano"
                        lat_lon = f"{lat_str} / {lon_str}"

                        # Globina z oznako "km"
                        depth = f"{latest.get('DEPTH')} km" if latest.get("DEPTH") is not None else "Neznano"

                        # Magnituda z eno decimalno natančnostjo in vejico
                        mag = format_decimal(latest.get("MAG1"))

                        # Največja intenziteta EMS-98: če je vrednost null, prikažemo "-"
                        intensity = latest.get("INTENZITETA") if latest.get("INTENZITETA") is not None else "-"

                        # Podatki so bili preverjeni s strani seizmologa: če REVISION == 1, potem DA, sicer NE
                        verified = "DA" if latest.get("REVISION") == 1 else "NE"

                        # Nastavimo stanje senzorja (state) kot opis nadžarišča
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
                            #"objectid": latest.get("OBJECTID")
                        }
        except Exception as e:
            _LOGGER.error("Prišlo je do izjeme pri async_update: %s", e)
