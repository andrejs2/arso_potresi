import logging
import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE

from .const import DOMAIN, DEFAULT_API_URL

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Vir: ARSO Potresi - Agencija RS za okolje"

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavi geolocation entiteto."""
    async_add_entities([ArsoPotresiGeolocation(config_entry)])

class ArsoPotresiGeolocation(Entity):
    """Končna entiteta za prikaz lokacije zadnjega potresa."""

    _attr_icon = "mdi:map-marker-radius"
    _attr_attribution = ATTRIBUTION

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Inicializiraj entiteto."""
        self._api_url = DEFAULT_API_URL
        self._name = "Zadnji potres (Lokacija)"
        self._unique_id = "arso_potresi_geolocation_final"
        
        self._latitude = None
        self._longitude = None
        self._state = None
        self._extra_attrs = {}

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        return self._state

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @property
    def extra_state_attributes(self):
        return self._extra_attrs

    async def async_update(self) -> None:
        """Osveži podatke in preveri, ali so koordinate nastavljene."""
        try:
            async with aiohttp.ClientSession() as session, async_timeout.timeout(15):
                response = await session.get(self._api_url)
                response.raise_for_status()
                all_earthquakes = await response.json()
        except Exception as e:
            _LOGGER.error("Napaka pri klicu na API: %s", e)
            return

        latest_valid = next((eq for eq in all_earthquakes if eq.get("LAT") and eq.get("LON") and eq.get("MAG1")), None)

        if not latest_valid:
            self._state = "Ni podatkov"
            return
            
        lat_val = latest_valid.get("LAT")
        lon_val = latest_valid.get("LON")
        mag_val = latest_valid.get("MAG1")
        
        try:
            self._latitude = float(lat_val)
            self._longitude = float(lon_val)
            self._state = float(mag_val)
            self._extra_attrs = {
                "Nadžarišče": latest_valid.get("GEOLOC", "Neznano"),
                ATTR_LATITUDE: self._latitude,
                ATTR_LONGITUDE: self._longitude
            }

        except (ValueError, TypeError) as e:
            _LOGGER.error("Napaka pri pretvorbi podatkov v float: %s", e)
            self._state = "Napaka pri obdelavi"
