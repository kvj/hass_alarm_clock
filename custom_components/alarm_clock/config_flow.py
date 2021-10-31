from homeassistant import config_entries
from homeassistant.const import (
    WEEKDAYS,
)
from homeassistant.util import dt
import homeassistant.helpers.config_validation as cv
from .constants import DOMAIN

import logging
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


def _gen_schema(user_input: dict, with_name: bool = True):
    wdays = {}
    for wday in WEEKDAYS:
        wdays[vol.Required(
            wday, default=user_input.get(wday, True))] = cv.boolean
    name_part = {}
    if with_name:
        name_part[vol.Required(
            "name",
            default=user_input.get("name", "Alarm Clock")
        )] = cv.string
    schema = vol.Schema({
        **name_part,
        vol.Required("time", default=user_input.get("time", "7:00")): cv.string,
        **wdays,
    })
    return schema


def _validate(inp):
    errors = dict()
    any_day_set = False
    for wday in WEEKDAYS:
        if inp.get(wday):
            any_day_set = True
    if not any_day_set:
        errors["mon"] = "no_days"
    time = dt.parse_time(inp.get("time"))
    if not time:
        errors["time"] = "invalid_time"
    return errors


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input):
        errors = None

        _LOGGER.debug(f"Input: {user_input}")
        if user_input:
            errors = _validate(user_input)
            if len(errors) == 0:
                return self.async_create_entry(
                    title=user_input.get("name"),
                    options=user_input,
                    data={},
                )

        if not user_input:
            user_input = dict()

        return self.async_show_form(
            step_id="user", data_schema=_gen_schema(user_input), errors=errors
        )

    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        _LOGGER.debug(f"OptionsFlowHandler: {user_input} {self.config_entry}")
        errors = None
        if user_input:
            errors = _validate(user_input)
            if len(errors) == 0:
                return self.async_create_entry(title="", data=user_input)
        else:
            user_input = self.config_entry.as_dict()["options"]

        return self.async_show_form(
            step_id="init", data_schema=_gen_schema(user_input, with_name=False), errors=errors
        )
