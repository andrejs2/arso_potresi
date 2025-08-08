import logging
from datetime import timedelta, datetime
import aiohttp
import async_timeout
import pytz

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.util.dt import parse_datetime
from homeassistant.components.sensor import SensorStateClass

from .const import DOMAIN, DEFAULT_API_URL, DEFAULT_SCAN_INTERVAL, DEFAULT_HISTORY_DAYS

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Vir: ARSO Potresi - Agencija RS za okolje"

def format_local_time(dt_obj):
    """Oblikuj datum v obliki: '6. 8. 2025 ob 16.49'."""
    if not dt_obj:
        return "Neznano"
    return f"{dt_obj.day}. {dt_obj.month}. {dt_obj.year} ob {dt_obj.hour:02d}.{dt_obj.minute:02d}"

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavi senzorje iz ARSO Potresi."""
    options = config_entry.options or config_entry.data
    scan_interval = timedelta(minutes=options.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    history_days = options.get("history_days", DEFAULT_HISTORY_DAYS)

    coordinator = ArsoDataCoordinator(hass, scan_interval, history_days)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        ArsoPotresiSensor(coordinator),
        ArsoPotresiMapSensor(coordinator)
    ], True)

class ArsoDataCoordinator:
    """Upravlja pridobivanje in shranjevanje podatkov."""
    def __init__(self, hass, scan_interval, history_days):
        self.hass = hass
        self.scan_interval = scan_interval
        self._history_days = history_days
        self._api_url = DEFAULT_API_URL
        self.data = None
        self._update_job = None

    async def _async_update_data(self):
        """Pridobi podatke iz API-ja."""
        try:
            async with aiohttp.ClientSession() as session, async_timeout.timeout(10):
                response = await session.get(self._api_url)
                response.raise_for_status()
                all_earthquakes = await response.json()
                
                now = datetime.now(pytz.utc)
                time_limit = now - timedelta(days=self._history_days)
                
                self.data = [e for e in all_earthquakes if parse_datetime(e.get("TIME")).astimezone(pytz.utc) >= time_limit]
        except Exception as e:
            _LOGGER.error("Napaka pri posodabljanju podatkov: %s", e)
            self.data = None

    async def async_config_entry_first_refresh(self):
        await self._async_update_data()
        
    async def async_update(self):
        await self._async_update_data()


class ArsoPotresiMapSensor(Entity):
    """Senzor, ki prikazuje magnitudo zadnjega potresa za prikaz na zemljevidu."""
    _attr_icon = "mdi:pulse"
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: ArsoDataCoordinator):
        self._coordinator = coordinator
        self._name = "Zadnji potres Magnituda"
        self._unique_id = "arso_potresi_map_sensor"
        self._state = None
        self._attrs = {}

    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._unique_id
    @property
    def state(self): return self._state
    @property
    def extra_state_attributes(self): return self._attrs
    @property
    def unit_of_measurement(self): return "M"
    @property
    def state_class(self): return SensorStateClass.MEASUREMENT
    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, "arso_potresi_device")}}

    async def async_update(self):
        await self._coordinator.async_update()
        if not self._coordinator.data:
            self._state = None
            return

        latest_valid = next((eq for eq in self._coordinator.data if eq.get("LAT") and eq.get("LON") and eq.get("MAG1")), None)
        
        if latest_valid:
            self._state = float(latest_valid["MAG1"])
            self._attrs[ATTR_LATITUDE] = float(latest_valid["LAT"])
            self._attrs[ATTR_LONGITUDE] = float(latest_valid["LON"])
            self._attrs["Nadžarišče"] = latest_valid.get("GEOLOC", "Neznano")
        else:
            self._state = None


class ArsoPotresiSensor(Entity):
    """Glavni senzor, ki prikazuje zadnji potres z vsemi podatki."""
    _attr_icon = "mdi:pulse"
    _attr_attribution = ATTRIBUTION
    
    def __init__(self, coordinator: ArsoDataCoordinator):
        self._coordinator = coordinator
        self._name = "ARSO Potresi"
        self._unique_id = "arso_potresi_sensor"
        self._state = "Neznano"
        self._attrs = {}

    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._unique_id
    @property
    def state(self): return self._state
    @property
    def extra_state_attributes(self): return self._attrs
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "arso_potresi_device")},
            "name": "ARSO Potresi",
            "manufacturer": "ARSO",
            "model": "Potresi",
            "entry_type": "service",
        }

    async def async_update(self):
        if not self._coordinator.data:
            self._state = "Ni podatkov"
            return
            
        latest = self._coordinator.data[0]
        self._state = latest.get("GEOLOC", "Neznano")

        all_attrs = {}
        for i, earthquake in enumerate(self._coordinator.data):
            dt_local = parse_datetime(earthquake.get("TIME"))
            try:
                dt_utc = pytz.UTC.localize(datetime.strptime(earthquake.get("TIME_ORIG"), "%Y-%m-%d %H:%M:%S"))
            except Exception:
                dt_utc = None
            
            lat_str = str(earthquake.get('LAT', '')).replace('.', ',')
            lon_str = str(earthquake.get('LON', '')).replace('.', ',')
            mag_str = str(earthquake.get('MAG1', '')).replace('.', ',')

            suffix = "" if i == 0 else f" {i}"
            
            if i > 0:
                all_attrs[f"--- Pretekli potres {i} ---"] = ""

            all_attrs[f"Lokalni čas potresa{suffix}"] = format_local_time(dt_local)
            all_attrs[f"Čas potresa v UTC{suffix}"] = format_local_time(dt_utc)
            all_attrs[f"Nadžarišče{suffix}"] = earthquake.get("GEOLOC", "Neznano")
            all_attrs[f"Zemljepisna širina/dolžina{suffix}"] = f"{lat_str} / {lon_str}" if lat_str and lon_str else "Neznano"
            all_attrs[f"Globina{suffix}"] = f"{earthquake.get('DEPTH')} km" if earthquake.get("DEPTH") is not None else "Neznano"
            all_attrs[f"Magnituda{suffix}"] = mag_str if mag_str else "Neznano"
            all_attrs[f"Največja intenziteta EMS-98{suffix}"] = earthquake.get("INTENZITETA") or "-"
            all_attrs[f"Preverjeno s strani seizmologa{suffix}"] = "DA" if earthquake.get("REVISION") == 1 else "NE"

        self._attrs = all_attrs
