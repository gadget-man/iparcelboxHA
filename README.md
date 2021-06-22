# iParcelBox Home Assistant Integeration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)


**This component will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show iParcelBox device statis with a variety of sensors (e.g. boxStatus, lidStatus, lockStatus, parcelCount, lastOpened).

## Installation
The easiest way to install it is through [HACS (Home Assistant Community Store)](https://github.com/hacs/integration),
search for <i>iParcelBox</i> in the Integrations.<br />
Note: Your iParcelBox needs to be online to complete the setup process. For battery-powered devices, we recommend that you press the iParcelBox button shortly before commencing the setup process.

## iParcelBox Premium Subscription
An iParcelBox Premium subscription is required to connect your iParcelBox device to Home Assistant. More details can be found at https://www.iparcelbox.com/faqs/#premium

## Configuration is done in the UI
This integration will auto-discover iParcelBox devices on your network. Simply select the device and enter the password from your iParcelBox Setup Instructions sticker. Alternatively you can manually add the integration and provide the relevant Serial Number, Mac Address and Password from your device.

## Lovelace UI
There is a Lovelace custom card related to this component in development! [https://github.com/gadget-man/iparcelbox-card](https://github.com/gadget-man/iparcelbox-card).


<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/blueprint.svg?style=for-the-badge
[commits]: https://github.com/gadget-man/iparcelboxHA/commits
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/custom-components/blueprint.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/custom-components/blueprint.svg?style=for-the-badge
[releases]: https://github.com/gadget-man/iparcelboxHA/releases
