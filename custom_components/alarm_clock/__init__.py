from os import stat
from .constants import DOMAIN, PLATFORMS


from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from homeassistant.const import (
    WEEKDAYS,
)

from homeassistant.util import dt

import logging
from datetime import (timedelta, datetime, date)

_LOGGER = logging.getLogger(__name__)


class Coordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry):
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._update,
            update_interval=timedelta(seconds=10)
        )
        self._weekday_map = {idx: value for idx, value in enumerate(WEEKDAYS)}

    @property
    def config(self):
        return self.entry.as_dict()["options"]

    @property
    def is_enabled(self):
        return self.entry.as_dict()["data"].get("enabled", True)

    async def set_enabled(self, enabled: bool):
        data = self.entry.as_dict()["data"]
        data["enabled"] = enabled
        self.hass.config_entries.async_update_entry(self.entry, data=data)
        await self.async_request_refresh()

    def _before_after(self, now):
        tm = dt.parse_time(self.config["time"])
        today = date.today()
        dates = [datetime.combine(today, tm)]
        for i in range(1, 8):
            dates.append(datetime.combine(today - timedelta(days=i), tm))
            dates.append(datetime.combine(today + timedelta(days=i), tm))
        dates_selected = list(
            sorted(filter(lambda x: self.config[self._weekday_map[x.weekday()]], dates)))
        for i in range(1, len(dates_selected)):
            if dates_selected[i-1] <= now < dates_selected[i]:
                return dates_selected[i-1], dates_selected[i]
        return None, None

    def _state_intervals(self, from_date, to_date, intervals):
        delta_mins = int((to_date - from_date).total_seconds() / 60)
        if delta_mins > intervals[0]:
            return None, None
        for i in range(1, len(intervals)):
            if intervals[i-1] > delta_mins >= intervals[i]:
                return intervals[i-1], intervals[i]
        return None, None

    async def _update(self):
        now = datetime.now()
        intervals = [30, 20, 10, 0]
        before, after = self._before_after(now)
        _LOGGER.debug(f"Next dates: {before}, {after} - {self.config}")
        before_start, before_end = self._state_intervals(
            now, after, intervals)
        after_start, after_end = self._state_intervals(before, now, intervals)
        state = "off"
        if after_start:
            if after_end == 0:
                state = "on"
            else:
                state = f"plus_{after_end}"
        elif before_start:
            state = f"minus_{before_start}"
        _LOGGER.debug(
            f"Next dates: {before}, {after} :: {state} [{before_start}-{before_end}]::[{after_start}-{after_end}] - {self.config}")
        return {
            "id": self.entry.entry_id,
            "name": self.entry.title,
            "minutes": int((after - now).total_seconds() / 60),
            "next": after,
            "state": state if self.is_enabled else "off"
        }


async def async_setup_entry(hass, entry):
    _LOGGER.debug(f"async_setup_entry: {entry}")
    coordinator = Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    # entry.async_on_unload(entry.add_update_listener(update_listener))

    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p))
    return True


async def async_unload_entry(hass, entry):
    _LOGGER.debug(f"async_unload_entry: {entry}")
    # await hass.data[DOMAIN][entry.entry_id].unload()
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

# async def update_listener(hass, entry):
#     _LOGGER.debug(f"update_listener: {entry}")


async def async_setup(hass, config) -> bool:
    hass.data[DOMAIN] = dict()

    return True


class AlarmClockEntity(CoordinatorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)

    def set_id(self, suffix: str):
        self.id_suffix = suffix

    def set_name(self, name: str):
        self._attr_name_suffix = name

    @property
    def name_suffix(self):
        return self._attr_name_suffix

    @property
    def get_name(self):
        return self.data["name"]

    @property
    def name(self) -> str:
        return "%s %s" % (self.get_name, self.name_suffix)

    @property
    def unique_id(self) -> str:
        return "%s-%s" % (self.data["id"], self.id_suffix)

    @property
    def data(self) -> dict:
        return self.coordinator.data

    @property
    def device_info(self):
        return {
            "identifiers": {("id", self.data["id"])},
            "name": self.get_name,
        }
