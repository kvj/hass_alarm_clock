from homeassistant.components.switch import SwitchEntity

import logging

from .constants import DOMAIN
from . import AlarmClockEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities.append(Active(coordinator))
    async_add_entities(entities)
    return True


class Active(AlarmClockEntity, SwitchEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.set_id("active")
        self.set_name("Active")

    @property
    def is_on(self):
        return self.coordinator.is_enabled

    async def async_turn_on(self, **kwargs):
        await self.coordinator.set_enabled(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.set_enabled(False)

    @property
    def icon(self):
        return "mdi:alarm" if self.is_on else "mdi:alarm-off"

    @property
    def entity_category(self):
        return "config"
