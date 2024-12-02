"""iParcelBox basic sensor entity for testing."""
from __future__ import annotations

import asyncio
import httpx
import async_timeout

from homeassistant.components.lock import LockEntityFeature
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.exceptions import ConfigEntryNotReady

# from homeassistant.util.async import (
#     run_callback_threadsafe, run_coroutine_threadsafe)


import logging

from .const import (
    DOMAIN,
    IPARCELBOX,
    IPARCELBOX_INFO,
    IPARCELBOX_API,
    IPARCELBOX_UPDATE_SIGNAL,
    SENSORS,
    IS_LOCKED,
    REQUEST_TIMEOUT,
)

from .entity import iParcelBoxEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the iParcelBox sensor platform."""
    # _LOGGER.debug("Starting Lock Entity setup")
    locks = []
    config_entry_id = config_entry.entry_id

    data = hass.data[DOMAIN][config_entry_id]
    iparcelbox = data[IPARCELBOX]
    iparcelbox_info = data[IPARCELBOX_INFO]
    iparcelbox_api = data[IPARCELBOX_API]

    # for sensor in SENSORS:
    #     # _LOGGER.debug("Need to add sensor: %s", sensor)

    #     sensor_object = iParcelBoxStatus(hass, iparcelbox, iparcelbox_info, sensor)
    #     sensors.append(sensor_object)

    
        
        # _LOGGER.debug("Attempting to add sensor: %s", sensor_object.name)
    lock = iParcelBoxObject(hass, iparcelbox, iparcelbox_info,iparcelbox_api)
    _LOGGER.debug("Need to add lock: %s", lock._unique_id)

    locks.append(lock)
    
    async_add_entities(locks)

def _allow_delivery(api):
    return api.allowDelivery()

def _lock_box(api):
    return api.lockBox()

def _empty_box(api):
    return api.emptyBox()


class iParcelBoxObject(iParcelBoxEntity, LockEntityFeature):
    """Representation of an iParcelBox device entity."""

    def __init__(self, hass, iparcelbox, iparcelbox_info,iparcelbox_api):
        """Initialize the entity."""
        
        super().__init__(iparcelbox, iparcelbox_info)
        self.hass = hass
        # self._sensor = sensor
        self._iparcelbox = iparcelbox
        self._api = iparcelbox_api
        # self._state = None
        self._unique_id = f"{self._iparcelbox._mac}"
        self._remove_signal_update = None
        self._lock_status = None
        self._box_status = None
        # _LOGGER.debug("Init sensor: %s", self._unique_id)
        # if sensor == BATTERY_LEVEL:
        #     self._device_class = DEVICE_CLASS_BATTERY
        #     self._state = 'Not installed'
        # if sensor == ASLEEP:
        #     self._state = 'N/A'

    @property
    def unique_id(self):
        """Sensor unique id."""
        return self._unique_id

    @property
    def should_poll(self):
        """Turn off polling for the lock status - local_push."""
        return False

    @property
    def name(self):
        """Return the name of the lock."""
        return f"{self._iparcelbox._name}"

    # @property
    # def state(self):
    #     """Return the state of the lock."""
    #     return self._state

    @property
    def is_locked(self):
        """Indication of whether the lock is currently locked. Used to determine state"""
        return True if self._lock_status == IS_LOCKED else False

    @property
    def supported_features(self):
        return LockEntityFeature.OPEN
        
    def update(self):
        """Fetch new state data for the lock.
        This is the only method that should fetch new data for Home Assistant.
        iParcelBox: don't do anything here - all updates via _update_callback
        """
        _LOGGER.debug("Lock update called")
        # raise NotImplementedError()

    def lock(self, **kwargs):
        """Lock all or specified locks. A code to lock the lock with may optionally be specified."""
        raise NotImplementedError()

    async def async_lock(self, **kwargs):
        """Lock all or specified locks. A code to lock the lock with may optionally be specified."""
        _LOGGER.debug("Call async lock")
        try:
            with async_timeout.timeout(REQUEST_TIMEOUT):
                result = await self.hass.async_add_executor_job(_lock_box, self._api)
        except (asyncio.TimeoutError) as err:
            _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", self._unique_id, err)
            raise ConfigEntryNotReady from err    
    
    def unlock(self, **kwargs):
        """Unlock all or specified locks. A code to unlock the lock with may optionally be specified."""
        raise NotImplementedError()

    async def async_unlock(self, **kwargs):
        """Unlock all or specified locks. A code to unlock the lock with may optionally be specified."""
        _LOGGER.debug("Call async unlock")
        try:
            with async_timeout.timeout(REQUEST_TIMEOUT):
                result = await self.hass.async_add_executor_job(_allow_delivery, self._api)
        except (asyncio.TimeoutError) as err:
            _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", self._unique_id, err)
            raise ConfigEntryNotReady from err    

    def open(self, **kwargs):
        """Open (unlatch) all or specified locks. A code to open the lock with may optionally be specified."""
        raise NotImplementedError()

    async def async_open(self, **kwargs):
        """Open (unlatch) all or specified locks. A code to open the lock with may optionally be specified."""
        _LOGGER.debug("Call async open")
        try:
            with async_timeout.timeout(REQUEST_TIMEOUT):
                result = await self.hass.async_add_executor_job(_empty_box, self._api)
        except (asyncio.TimeoutError) as err:
            _LOGGER.error("TimeoutError connecting to iParcelBox at %s (%s)", self._unique_id, err)
            raise ConfigEntryNotReady from err    
    
    async def async_added_to_hass(self):
        """Call when entity is added to hass."""
        self._remove_signal_update = async_dispatcher_connect(
            self.hass,
            IPARCELBOX_UPDATE_SIGNAL.format(self._iparcelbox._mac),
            self._update_callback,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Call when entity will be removed from hass."""
        self._remove_signal_update()


    @callback
    def _update_callback(self, data):
        """Call update method."""
        _LOGGER.debug("iParcelBox Lock callback: %s", data["lockStatus"])
        # self._state = True if data["lockStatus"] == "locked" else False
        self._lock_status = data["lockStatus"]
        self._box_status = data["boxStatus"]
        # self._state = data["lockStatus"]
        self.async_schedule_update_ha_state(True)

    
# @asyncio.coroutine
# def _async_getStatus(device):
#     return device.getStatus()
