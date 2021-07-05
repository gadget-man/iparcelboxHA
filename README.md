# iParcelBox Home Assistant Integration

[![GH-release](https://img.shields.io/github/v/release/gadget-man/iparcelboxHA.svg?style=plastic)](https://github.com/gadget-man/iparcelboxHA/releases)
[![GH-downloads](https://img.shields.io/github/downloads/gadget-man/iparcelboxHA/total?style=plastic)](https://github.com/gadget-man/iparcelboxHA/releases)
[![GH-last-commit](https://img.shields.io/github/last-commit/gadget-man/iparcelboxHA.svg?style=plastic)](https://github.com/gadget-man/iparcelboxHA/commits/master)
[![GH-code-size](https://img.shields.io/github/languages/code-size/gadget-man/iparcelboxHA.svg?color=red&style=plastic)](https://github.com/gadget-man/iparcelboxHA)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=plastic)](https://github.com/hacs)


<img style="border: 5px solid #767676;border-radius: 10px;max-width: 350px;width: 100%;box-sizing: border-box;" src="https://github.com/gadget-man/iparcelbox-card/blob/master/examples/Screenshot.png" alt="Screenshot">


**This component will set up the following platforms.**

Platform | Description
-- | --
`lock` | Provide lock entity to allow services to be called to Allow Delivery, Empty Box and Lock Box.
`sensor` | Show iParcelBox device sensor status (boxStatus, parcelCount, lastOpened, Wifi details, battery level).
`binary_sensor` | Show iParcelBox device binary sensor status (lockStatus, lidStatus, sleep mode, battery charging indicator).

## Installation

iParcelBox custom integration is available from [HACS][hacs] as a custom repository.
In your HA HACS dashboard, select 'Integrations', then select the 3 dots in the top right corner of the screen and choose 'Custom Repositories'.
Enter `https://github.com/gadget-man/iparcelboxHA` and select `Integration` as the category.

Note: Your iParcelBox needs to be online to complete the setup process. For battery-powered devices, we recommend that you press the iParcelBox button shortly before commencing the setup process.

## Configuration is done in the UI
This integration will auto-discover iParcelBox devices on your network. Simply select the device and enter the password from your iParcelBox Setup Instructions sticker. Alternatively you can manually add the integration and provide the relevant Serial Number, Mac Address and Password from your device.

## Lovelace UI
There is a Lovelace custom card related to this component, available at [https://github.com/gadget-man/iparcelbox-card](https://github.com/gadget-man/iparcelbox-card).

## iParcelBox Premium Subscription
An iParcelBox Premium subscription is required to connect your iParcelBox device to Home Assistant. More details can be found at https://www.iparcelbox.com/faqs/#premium

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/blueprint.svg?style=plastic
[commits]: https://github.com/gadget-man/iparcelboxHA/commits
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=plastic
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=plastic
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/custom-components/blueprint.svg?style=plastic
[releases-shield]: https://img.shields.io/github/release/custom-components/blueprint.svg?style=plastic
[releases]: https://github.com/gadget-man/iparcelboxHA/releases
