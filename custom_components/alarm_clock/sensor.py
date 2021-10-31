from homeassistant.components.sensor import SensorEntity

import logging

from .constants import DOMAIN
from . import AlarmClockEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities.append(State(coordinator))
    entities.append(NextAlarm(coordinator))
    async_add_entities(entities)
    return True


class State(AlarmClockEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.set_id("state")
        self.set_name("State")

    @property
    def state(self):
        return self.data["state"]

    @property
    def icon(self):
        if self.state == "off":
            return "mdi:alarm-off"
        elif self.state == "on":
            return "mdi:alarm-check"
        else:
            return "mdi:alarm"


class NextAlarm(AlarmClockEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.set_id("next")
        self.set_name("Next Alarm")
        self._attr_device_class = "timestamp"

    @property
    def state(self):
        return self.data["next"] if self.coordinator.is_enabled else None

    @property
    def extra_state_attributes(self):
        return {
            "minutes": self.data["minutes"]
        } if self.coordinator.is_enabled else None

    @property
    def entity_category(self):
        return "diagnostic"
