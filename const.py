"""Constants for the iParcelBox (Beta) integration."""

DOMAIN = "iparcelbox"
MANUFACTURER = "iParcelBox Ltd"

IPARCELBOX = "iparcelbox"
IPARCELBOX_INFO = "iparcelbox_info"
IPARCELBOX_API = "api"

IPARCELBOX_INFO_KEY_FIRMWARE = "fw_version"
IPARCELBOX_MAC_ADRESS = "mac"

PLATFORMS = ["lock", "sensor", "binary_sensor"]

IPARCELBOX_UPDATE_SIGNAL="iparcelbox_update_{}"
# IPARCELBOX_UPDATE_SIGNAL="iparcelbox_update"

CONF_SERIAL = "serial"
CONF_WEBHOOK_URL = "webhook_url"

REQUEST_TIMEOUT = 10

IS_LOCKED = "locked"

# Services
BOX_STATUS = "boxStatus"
LOCK_STATUS = "lockStatus"
LID_STATUS = "lidStatus"
PARCEL_COUNT = "parcelCount"
LAST_OPENED = "lastOpened"
ROUTER_RSSI = "routerRSSI"
ROUTER_SSID = "routerSSID"
BATTERY_LEVEL = "battery"
BATTERY_CHARGING = "charging"
ASLEEP = "asleep"

SENSORS = [
    BOX_STATUS,
    PARCEL_COUNT,
    LAST_OPENED,
    ROUTER_RSSI,
    ROUTER_SSID,
    BATTERY_LEVEL,
]

BINARY_SENSORS = [
    LOCK_STATUS,
    LID_STATUS,
    ASLEEP,
    BATTERY_CHARGING,
]

SERVICE_ALLOW_DELIVERY = "allowdelivery"
SERVICE_EMPTY_BOX = "emptybox"
SERVICE_LOCK_BOX = "lockbox"
SERVICES = [
    SERVICE_ALLOW_DELIVERY,
    SERVICE_EMPTY_BOX,
    SERVICE_LOCK_BOX,
]
