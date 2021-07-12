"""iParcelBox basic sensor entity for testing."""
from __future__ import annotations

import asyncio
import httpx

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import PERCENTAGE, DEVICE_CLASS_BATTERY, DEVICE_CLASS_TIMESTAMP
from homeassistant.helpers.httpx_client import get_async_client

# from homeassistant.util.async import (
#     run_callback_threadsafe, run_coroutine_threadsafe)


import logging

from .const import (
    DOMAIN,
    IPARCELBOX,
    IPARCELBOX_INFO,
    IPARCELBOX_UPDATE_SIGNAL,
    SENSORS,
    BATTERY_LEVEL,
    ROUTER_RSSI,
    LAST_OPENED
)

from .entity import iParcelBoxEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the iParcelBox sensor platform."""
    sensors = []
    config_entry_id = config_entry.entry_id

    data = hass.data[DOMAIN][config_entry_id]
    iparcelbox = data[IPARCELBOX]
    iparcelbox_info = data[IPARCELBOX_INFO]

    for sensor in SENSORS:
        _LOGGER.debug("Need to add sensor: %s", sensor)

        sensor_object = iParcelBoxStatus(hass, iparcelbox, iparcelbox_info, sensor)
        sensors.append(sensor_object)

    
        
        # _LOGGER.debug("Attempting to add sensor: %s", sensor_object.name)

    async_add_entities(sensors)



class iParcelBoxStatus(iParcelBoxEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, iparcelbox, iparcelbox_info, sensor):
        """Initialize the sensor."""
        
        super().__init__(iparcelbox, iparcelbox_info)
        self.hass = hass
        self._sensor = sensor
        self._iparcelbox = iparcelbox
        self._state = None
        self._device_class = None
        self._unique_id = f"{self._iparcelbox._mac}-{sensor}"
        self._remove_signal_update = None
        # _LOGGER.debug("Init sensor: %s", self._unique_id)
        if sensor == BATTERY_LEVEL:
            self._device_class = DEVICE_CLASS_BATTERY
            self._state = 'Not installed'


    @property
    def unique_id(self):
        """Sensor unique id."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._iparcelbox._name} {self._sensor}"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._sensor == ROUTER_RSSI:
            return PERCENTAGE
        if self._sensor == BATTERY_LEVEL and self._state != 'Not installed':
            return PERCENTAGE
        
    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        iParcelBox: don't do anything here - all updates via _update_callback
        """
        # _LOGGER.debug("Calling getStatus")
        # self._state = asyncio.run_coroutine_threadsafe(
        #     self.async_update(), self.hass.loop
        # ).result()
        # self._state = "Locked"
    
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
        if (data[self._sensor]!= ''):
            """Call update method."""
            _LOGGER.debug("iParcelBox Sensor callback: %s", data[self._sensor])
            self._state = data[self._sensor]
            self.async_schedule_update_ha_state(True)

    
# @asyncio.coroutine
# def _async_getStatus(device):
#     return device.getStatus()
