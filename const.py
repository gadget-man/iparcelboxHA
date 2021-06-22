"""Constants for the iParcelBox (Beta) integration."""

DOMAIN = "iparcelbox"
MANUFACTURER = "iParcelBox Ltd"

IPARCELBOX = "iparcelbox"
IPARCELBOX_INFO = "iparcelbox_info"
IPARCELBOX_API = "api"

IPARCELBOX_INFO_KEY_FIRMWARE = "fw_version"
IPARCELBOX_MAC_ADRESS = "mac"

IPARCELBOX_UPDATE_SIGNAL="iparcelbox_update_{}"
# IPARCELBOX_UPDATE_SIGNAL="iparcelbox_update"

CONF_SERIAL = "serial"
CONF_WEBHOOK_URL = "webhook_url"

REQUEST_TIMEOUT = 10

# Services
BOX_STATUS = "boxStatus"
LOCK_STATUS = "lockStatus"
LID_STATUS = "lidStatus"
CONNECTED = "connected"
PARCEL_COUNT = "parcelCount"
LAST_OPENED = "lastOpened"
ROUTER_RSSI = "routerRSSI"
ROUTER_SSID = "routerSSID"
BATTERY_LEVEL = "battery"
ASLEEP = "asleep"

SENSORS = [
    BOX_STATUS,
    LOCK_STATUS,
    LID_STATUS,
    CONNECTED,
    PARCEL_COUNT,
    LAST_OPENED,
    ROUTER_RSSI,
    ROUTER_SSID,
    BATTERY_LEVEL,
    ASLEEP,
]

SERVICE_ALLOW_DELIVERY = "allowdelivery"
SERVICE_EMPTY_BOX = "emptybox"
SERVICE_LOCK_BOX = "lockbox"
SERVICES = [
    SERVICE_ALLOW_DELIVERY,
    SERVICE_EMPTY_BOX,
    SERVICE_LOCK_BOX,
]
