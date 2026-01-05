"""Config flow for iParcelBox (Beta) integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from iparcelboxpy import iParcelBox
import requests
import asyncio
import async_timeout

from http import HTTPStatus
from homeassistant import config_entries
from homeassistant import core
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_MAC
)

from .const import (
    DOMAIN,
    CONF_SERIAL,
    REQUEST_TIMEOUT,
    CONF_WEBHOOK_ID,
    CONF_WEBHOOK_URL
)

_LOGGER = logging.getLogger(__name__)


def _discovery_schema_with_defaults(discovery_info: DiscoveryInfoType) -> vol.Schema:
    return vol.Schema(_ordered_shared_schema(discovery_info))

def _user_schema_with_defaults(user_input: dict[str, Any]) -> vol.Schema:
    user_schema = {
        vol.Required(CONF_SERIAL, default=user_input.get(CONF_SERIAL, "")): str,
        vol.Required(CONF_MAC, default=user_input.get(CONF_MAC, "")): str,
    }
    user_schema.update(_ordered_shared_schema(user_input))

    return vol.Schema(user_schema)

def _ordered_shared_schema(
    schema_input: dict[str, Any]
) -> dict[vol.Required | vol.Optional, Any]:
    return {
        vol.Required(CONF_PASSWORD, default=schema_input.get(CONF_PASSWORD, "")): str,
        }


def _init_iparcelbox_device(device):
    return device.getInfo(), device.getStatus()

class IParcelBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iParcelBox (Beta)."""

    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize the iParcelBox config flow."""
        self.saved_user_input: dict[str, Any] = {}
        self.discovered_conf: dict[str, Any] = {}

    async def _show_setup_form(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, str] | None = None,
    ) -> FlowResult:
        """Show the setup form to the user."""
        _LOGGER.debug("Showing Setup Form")
        if not user_input:
            user_input = {}

        if self.discovered_conf:
            user_input.update(self.discovered_conf)
            step_id = "link"
            data_schema = _discovery_schema_with_defaults(user_input)
        else:
            step_id = "user"
            data_schema = _user_schema_with_defaults(user_input)

        return self.async_show_form(
            step_id=step_id,
            data_schema=data_schema,
            errors=errors or {},
            description_placeholders=self.discovered_conf or {},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return await self._show_setup_form(user_input, None)

        if self.discovered_conf:
            user_input.update(self.discovered_conf)
            hostname = user_input[CONF_HOST]
            name = user_input[CONF_NAME]
        else:
            hostname = "iParcelBox-" + user_input[CONF_SERIAL]
            name = ("iParcelBox-" + user_input[CONF_SERIAL])

        password = user_input[CONF_PASSWORD]

        _LOGGER.debug("CONF_HOST: %s", hostname)
        _LOGGER.debug("CONF_SERIAL: %s", user_input[CONF_SERIAL])
        _LOGGER.debug("CONF_MAC: %s", user_input[CONF_MAC])
        _LOGGER.debug("CONF_NAME: %s", name)
        # _LOGGER.debug("CONF_PASSWORD: %s", password)

        errors = {}
        info = {}
        status = {}

        device = iParcelBox(hostname, password)
        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                info, status = await self.hass.async_add_executor_job(_init_iparcelbox_device, device)
        except (asyncio.TimeoutError) as err:
            _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", hostname, err)
            errors["base"] = "cannot_connect"
        except requests.exceptions.HTTPError as err:
            _LOGGER.debug("Connection error")
            _LOGGER.debug(err.response.status_code)
            if err.response.status_code == HTTPStatus.UNAUTHORIZED:
                errors["base"] = "invalid_auth"
            errors["base"] = "cannot_connect"
        except OSError as err:
            errors["base"] = "cannot_connect"

        if info and not info[0]:
            if info[1] == 401:
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"

        if status:
            _LOGGER.debug("Got Status: %s", status)
            if not status["result"]:
                _LOGGER.debug("Status message: %s", status["message"])
                return self.async_abort(reason="not_licenced")

        if errors:
            self.discovered_conf = {
                CONF_HOST: hostname,
                CONF_SERIAL: user_input[CONF_SERIAL],
                CONF_MAC: user_input[CONF_MAC],
                CONF_NAME: name,
            }
            self.context["title_placeholders"] = self.discovered_conf
            return await self._show_setup_form(user_input, errors)
           
        config_data = {
            CONF_HOST: hostname,
            CONF_SERIAL: user_input[CONF_SERIAL],
            CONF_MAC: user_input[CONF_MAC],
            CONF_NAME: name,
            CONF_PASSWORD: user_input[CONF_PASSWORD],
        }

        return self.async_create_entry(title=name, data=config_data)

        
    async def async_step_link(self, user_input: dict[str, Any]) -> FlowResult:
        """Link a config entry from discovery."""
        return await self.async_step_user(user_input)

    async def  async_step_zeroconf(self, info) -> FlowResult:
        _LOGGER.debug("iParcelBox device found via ZeroConf: %s", info.name) 
        #_LOGGER.debug(info)
        #TODO: IF DEVICE ALREADY REGISTERED, CHECK THAT HOST HASN'T CHANGED
        
        hostname = info.host
        serial = info.properties["serial"]
        mac = info.properties["mac"].upper()
        name = info.name.replace('._iparcelbox._tcp.local.', '')

        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()

        _LOGGER.debug("Got hostname from ZeroConf: %s", hostname)

        self.discovered_conf = {
            CONF_HOST: hostname,
            CONF_SERIAL: serial,
            CONF_MAC: mac,
            CONF_NAME: name
        }
        # _LOGGER.debug(mac)

        self.context["title_placeholders"] = self.discovered_conf
        return await self.async_step_user()
    
    async def async_get_options_flow(self, config_entry):
        return IParcelBoxOptionsFlowHandler(config_entry)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
    
class IParcelBoxOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            if user_input.get("reset_webhook"):
                data = dict(self.entry.data)
                data.pop(CONF_WEBHOOK_ID, None)
                data.pop(CONF_WEBHOOK_URL, None)

                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data=data,
                )

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("reset_webhook", default=False): bool,
            }),
        )
