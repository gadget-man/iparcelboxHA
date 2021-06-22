"""The iParcelBox integration base entity."""

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import Entity

import logging

from homeassistant.const import (
    CONF_MAC,
)

from .const import (
    DOMAIN,
    MANUFACTURER,
    IPARCELBOX,
    IPARCELBOX_INFO,
    IPARCELBOX_INFO_KEY_FIRMWARE,
)
# from .util import get_mac_address_from_doorstation_info

_LOGGER = logging.getLogger(__name__)


class iParcelBoxEntity(Entity):
    """Base class for iParcelBox entities."""

    def __init__(self, iparcelbox, iparcelbox_info):
        """Initialize the entity."""
        super().__init__()
        self._iparcelbox_info = iparcelbox_info
        self._iparcelbox = iparcelbox
        # _LOGGER.debug("iParcelBoxEntity Init: %s", iparcelbox_info[IPARCELBOX_INFO_KEY_FIRMWARE])

        # print(iparcelbox[CONF_MAC])

        # _LOGGER.debug("GOT IPARCELBOX to entity.py: %s", self._iparcelbox)
        # self._mac_addr = get_mac_address_from_doorstation_info(doorstation_info)


    @property
    def device_info(self):
        """iParcelBox device info."""
        firmware = self._iparcelbox_info[IPARCELBOX_INFO_KEY_FIRMWARE]
        # _LOGGER.debug("iParcelBoxEntity Device_Info: %s", firmware)
        self._mac_addr = self._iparcelbox._mac
        # print(self._mac_addr)
        # _LOGGER.debug("GOT IPARCELBOX mac to entity.py: %s", self._mac_addr)

        # firmware_build = self._doorstation_info[DOORBIRD_INFO_KEY_BUILD_NUMBER]
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac_addr)},
            # "identifiers": {(DOMAIN, self._iparcelbox._serial)},
            "name": self._iparcelbox._name,
            "manufacturer": MANUFACTURER,
            "model": self._mac_addr,
            "sw_version": {firmware},
            # "model": self._doorstation_info[DOORBIRD_INFO_KEY_DEVICE_TYPE],
        }