import logging
from datetime import timedelta, datetime
import async_timeout
import pytz

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
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


class ArsoDataCoordinator(DataUpdateCoordinator):
    """Koordinator za pridobivanje podatkov o potresih iz ARSO API-ja."""

    def __init__(self, hass: HomeAssistant, scan_interval: int, history_days: int) -> None:
        """Inicializiraj koordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="ARSO Potresi",
            update_interval=timedelta(minutes=scan_interval),
        )
        self._history_days = history_days
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> list[dict]:
        """Pridobi podatke iz ARSO API-ja."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(DEFAULT_API_URL)
                response.raise_for_status()
                all_earthquakes = await response.json()
        except Exception as err:
            raise UpdateFailed(f"Napaka pri pridobivanju podatkov: {err}") from err

        now = datetime.now(pytz.utc)
        time_limit = now - timedelta(days=self._history_days)

        filtered = []
        for e in all_earthquakes:
            time_str = e.get("TIME")
            if not time_str:
                continue
            dt = parse_datetime(time_str)
            if dt and dt.astimezone(pytz.utc) >= time_limit:
                filtered.append(e)
        return filtered


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Nastavi senzorje iz ARSO Potresi."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities([
        ArsoPotresiSensor(coordinator),
        ArsoPotresiMapSensor(coordinator),
    ])


class ArsoPotresiMapSensor(CoordinatorEntity):
    """Senzor, ki prikazuje magnitudo zadnjega potresa za prikaz na zemljevidu."""

    _attr_icon = "mdi:pulse"
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: ArsoDataCoordinator) -> None:
        """Inicializiraj senzor."""
        super().__init__(coordinator)
        self._attr_name = "Zadnji potres Magnituda"
        self._attr_unique_id = "arso_potresi_map_sensor"

    @property
    def state(self):
        """Vrni magnitudo zadnjega potresa."""
        if not self.coordinator.data:
            return None
        latest = next(
            (eq for eq in self.coordinator.data
             if eq.get("LAT") and eq.get("LON") and eq.get("MAG1")),
            None,
        )
        return float(latest["MAG1"]) if latest else None

    @property
    def unit_of_measurement(self):
        return "M"

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self):
        """Vrni dodatne atribute."""
        if not self.coordinator.data:
            return {}
        latest = next(
            (eq for eq in self.coordinator.data
             if eq.get("LAT") and eq.get("LON") and eq.get("MAG1")),
            None,
        )
        if not latest:
            return {}
        return {
            ATTR_LATITUDE: float(latest["LAT"]),
            ATTR_LONGITUDE: float(latest["LON"]),
            "Nadžarišče": latest.get("GEOLOC", "Neznano"),
        }

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, "arso_potresi_device")}}


class ArsoPotresiSensor(CoordinatorEntity):
    """Glavni senzor, ki prikazuje zadnji potres z vsemi podatki."""

    _attr_icon = "mdi:pulse"
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: ArsoDataCoordinator) -> None:
        """Inicializiraj senzor."""
        super().__init__(coordinator)
        self._attr_name = "ARSO Potresi"
        self._attr_unique_id = "arso_potresi_sensor"

    @property
    def state(self):
        """Vrni lokacijo zadnjega potresa."""
        if not self.coordinator.data:
            return "Ni podatkov"
        return self.coordinator.data[0].get("GEOLOC", "Neznano")

    @property
    def extra_state_attributes(self):
        """Vrni atribute vseh potresov."""
        if not self.coordinator.data:
            return {}

        all_attrs = {}
        for i, earthquake in enumerate(self.coordinator.data):
            dt_local = parse_datetime(earthquake.get("TIME"))
            try:
                dt_utc = pytz.UTC.localize(
                    datetime.strptime(earthquake.get("TIME_ORIG"), "%Y-%m-%d %H:%M:%S")
                )
            except Exception:
                dt_utc = None

            lat_str = str(earthquake.get("LAT", "")).replace(".", ",")
            lon_str = str(earthquake.get("LON", "")).replace(".", ",")
            mag_str = str(earthquake.get("MAG1", "")).replace(".", ",")

            suffix = "" if i == 0 else f" {i}"

            if i > 0:
                all_attrs[f"--- Pretekli potres {i} ---"] = ""

            all_attrs[f"Lokalni čas potresa{suffix}"] = format_local_time(dt_local)
            all_attrs[f"Čas potresa v UTC{suffix}"] = format_local_time(dt_utc)
            all_attrs[f"Nadžarišče{suffix}"] = earthquake.get("GEOLOC", "Neznano")
            all_attrs[f"Zemljepisna širina/dolžina{suffix}"] = (
                f"{lat_str} / {lon_str}" if lat_str and lon_str else "Neznano"
            )
            all_attrs[f"Globina{suffix}"] = (
                f"{earthquake.get('DEPTH')} km"
                if earthquake.get("DEPTH") is not None
                else "Neznano"
            )
            all_attrs[f"Magnituda{suffix}"] = mag_str if mag_str else "Neznano"
            all_attrs[f"Največja intenziteta EMS-98{suffix}"] = (
                earthquake.get("INTENZITETA") or "-"
            )
            all_attrs[f"Preverjeno s strani seizmologa{suffix}"] = (
                "DA" if earthquake.get("REVISION") == 1 else "NE"
            )

        return all_attrs

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "arso_potresi_device")},
            "name": "ARSO Potresi",
            "manufacturer": "ARSO",
            "model": "Potresi",
            "entry_type": "service",
        }
