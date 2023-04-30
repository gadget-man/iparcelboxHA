"""The iParcelBox (Beta) integration."""
from __future__ import annotations

from iparcelboxpy import iParcelBox

import logging
import requests
from . import const
import asyncio
import async_timeout
from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.util import dt as dt_util, slugify
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_MAC,
    CONF_PASSWORD,
    CONF_WEBHOOK_ID
)
from http import HTTPStatus

from .sensor import iParcelBoxStatus

from .const import (
    DOMAIN, 
    MANUFACTURER,
    IPARCELBOX,
    IPARCELBOX_INFO,
    IPARCELBOX_API,
    PLATFORMS,
    IPARCELBOX_INFO_KEY_FIRMWARE,
    CONF_SERIAL,
    CONF_WEBHOOK_URL,
    IPARCELBOX_UPDATE_SIGNAL,
    IPARCELBOX_MESSAGE_SIGNAL,
    SERVICES,
    SERVICE_ALLOW_DELIVERY,
    SERVICE_EMPTY_BOX,
    SERVICE_LOCK_BOX,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iParcelBox from a config entry."""
    config_updates = {}
    
    if not DOMAIN in hass.data:
        hass.data[DOMAIN] = {}

    iparcelbox_config = entry.data
    config_entry_id = entry.entry_id
    name = iparcelbox_config[CONF_NAME]
    _LOGGER.debug("Setup iParcelBox : %s",name)

    hostname = iparcelbox_config[CONF_HOST]
    serial = iparcelbox_config[CONF_SERIAL]
    mac = iparcelbox_config[CONF_MAC]
    password = iparcelbox_config[CONF_PASSWORD]
    device = iParcelBox(hostname, password)  #Initialises iParcelBoxPy instance


    _LOGGER.debug("Connecting to device host: %s",hostname)
    try:
        with async_timeout.timeout(REQUEST_TIMEOUT):
            status, info = await hass.async_add_executor_job(_init_iparcelbox_device, device)
    except (asyncio.TimeoutError) as err:
        _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", hostname, err)
        raise ConfigEntryNotReady from err
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == HTTPStatus.UNAUTHORIZED:
            _LOGGER.error(
                "Authorization rejected by iParcelBox for %s@%s", hostname, password
            )
            return False
        _LOGGER.error(
                "Unable to connect to iParcelBox for %s@%s", hostname, password
            )
        raise ConfigEntryNotReady from err
    except OSError as oserr:
        _LOGGER.error("Failed to setup iParcelBox at %s: %s", hostname, oserr)
        raise ConfigEntryNotReady from oserr

    if not info[0]:
        _LOGGER.error(
            "Could not connect to iParcelBox as %s@%s: Error %s",
            hostname,
            password,
            str(info[1]),
        )
        return False


    _LOGGER.debug("Got status from device: Result: %s, Message: %s", str(status["result"]), status["message"])

    iparcelbox = ConfigureiParcelBox(device, name, hostname, mac, serial)

    hass.data[DOMAIN][entry.entry_id] = {
        IPARCELBOX: iparcelbox,
        IPARCELBOX_INFO: info[1],
        IPARCELBOX_API: device,        
    }

    # Services
    # await _async_setup_services(hass) #not needed - lock, unlock & open services set as part of lock platform

    _LOGGER.debug("Setting up Platform")
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


    if CONF_WEBHOOK_ID not in entry.data:
        webhook_id = webhook.async_generate_id()
        webhook_url = webhook.async_generate_url(hass, webhook_id)

        config_updates["data"] = {
            **entry.data,
            **{
                CONF_WEBHOOK_ID: webhook_id,
                CONF_WEBHOOK_URL: webhook_url,
            },
        }
    else:
        webhook_id = iparcelbox_config[CONF_WEBHOOK_ID]
        webhook_url = iparcelbox_config[CONF_WEBHOOK_URL]

    if config_updates:
        hass.config_entries.async_update_entry(entry, **config_updates)
    
    _LOGGER.debug("Attempting to register webhook: DOMAIN: %s, ID: %s", const.DOMAIN, webhook_id)
    _LOGGER.debug("Webhook URL: %s", webhook_url)
    
    try:
        _LOGGER.debug("Setting up webhook: %s, %s", device, webhook_url)
        webhook.async_register(
            hass,
            const.DOMAIN,
            "iParcelBox notify",
            webhook_id,
            async_webhook_handler,
        )
    except:
        _LOGGER.error("Unable to create new webhook, may already exist")
    
    try:
        with async_timeout.timeout(REQUEST_TIMEOUT):
            result = await hass.async_add_executor_job(_init_iparcelbox_webhook, device, webhook_url)
    except (asyncio.TimeoutError) as err:
        _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", hostname, err)
        raise ConfigEntryNotReady from err
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == HTTPStatus.UNAUTHORIZED:
            _LOGGER.error(
                "Authorization rejected by iParcelBox for %s@%s", hostname, password
            )
            return False
        raise ConfigEntryNotReady from err
    except OSError as oserr:
        _LOGGER.error("Failed to setup iParcelBox webhook at %s: %s", hostname, oserr)
        raise ConfigEntryNotReady from oserr

    _LOGGER.debug("Setup webhook response: %s", result)

    return True


def _init_iparcelbox_device(device):
    return device.getStatus(), device.getInfo()

def _init_iparcelbox_webhook(device, url):
    # _LOGGER.debug("Starting setwebhook: %s", url)
    return device.setWebhook(url)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_webhook_handler(
    hass: HomeAssistant, webhook_id: str, request: Request
) -> Response | None:
    """Handle webhooks calls."""

    body = await request.json()
    _LOGGER.debug("Webhook RCPT %s: %s", body["device"], body["message"])
    # _LOGGER.debug(body["data"])
    data = {}
    data["message"] = body["message"]
    async_dispatcher_send(hass, IPARCELBOX_UPDATE_SIGNAL.format(body["device"]), body["data"])
    async_dispatcher_send(hass, IPARCELBOX_MESSAGE_SIGNAL.format(body["device"]), data)


async def _async_setup_services(hass: HomeAssistant) -> None:  #not needed - lock, unlock & open services set as part of lock platform
    """Service handler setup."""

    # _LOGGER.debug("Called setup services")   
    async def service_handler(call: ServiceCall) -> None:
        """Handle service call."""
        serial = call.data.get(CONF_SERIAL)
        devices = hass.data[DOMAIN]

        if serial:
            # _LOGGER.debug("Searching for devices to match: %s", serial)
            device = []
            for devicelist in devices:
                if serial == devices[devicelist][IPARCELBOX]._serial:
                    device = devices.get(devicelist)
        elif len(devices) == 1:
            device = next(iter(devices.values()))
            serial = next(iter(devices))
        else:
            _LOGGER.error(
                "More than one iParcelBox configured, must specify one of serials %s",
                sorted(devices),
            )
            return
        
        if not device:
            _LOGGER.error("iParcelBox with specified serial %s not found", serial)
            return

        api = device[IPARCELBOX_API]
        iparcelbox = device[IPARCELBOX]
        # _LOGGER.debug("Service found device: %s", iparcelbox._name)
        try:
            with async_timeout.timeout(REQUEST_TIMEOUT):
                result = await hass.async_add_executor_job(call_iparcelbox_action, api, call.service)
        except (asyncio.TimeoutError) as err:
            _LOGGER.error("TimeoutError sending command to iParcelBox-%s (%s)", serial, err)
            raise ConfigEntryNotReady from err
            # return False
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == HTTPStatus.UNAUTHORIZED:
                _LOGGER.error(
                    "Authorization rejected by iParcelBox for %s", iparcelbox._hostname
                )
                return False
            raise ConfigEntryNotReady from err
        except OSError as oserr:
            _LOGGER.error("Failed to setup iParcelBox webhook at %s: %s", iparcelbox._hostname, oserr)
            raise ConfigEntryNotReady from oserr

        _LOGGER.debug("API response: %s", result["message"])

    for service in SERVICES:
        hass.services.async_register(DOMAIN, service, service_handler)

def call_iparcelbox_action(api, action):
    if action == SERVICE_ALLOW_DELIVERY:
        return api.allowDelivery()
    elif action == SERVICE_EMPTY_BOX:
        return api.emptyBox()
    elif action == SERVICE_LOCK_BOX:
        return api.lockBox()

class ConfigureiParcelBox:
    """Attach additional information to pass along with configured device."""

    def __init__(self, device, name, hostname, mac, serial):
        """Initialize configured device."""
        self._name = name
        self._device = device
        self._hostname = hostname
        self._mac = mac
        self._serial = serial

    @property
    def name(self):
        """Get custom device name."""
        return self._name

    @property
    def device(self):
        """Get the configured device."""
        return self._device

    @property
    def hostname(self):
        """Get the configured hostname."""
        return self._hostname
    
    @property
    def mac(self):
        """Get the configured mac addrress."""
        return self._mac

    @property
    def serial(self):
        """Get the configured serial number."""
        return self._serial

    @property
    def slug(self):
        """Get device slug."""
        return slugify(self._name)