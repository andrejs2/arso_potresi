<div align="center">
  <a href="https://potresi.arso.gov.si/">
    <img 
      src="https://raw.githubusercontent.com/andrejs2/arso_potresi/main/images/logo%402x.png" 
      alt="ARSO Potresi Logo" 
      width="300"
    />
  </a>
</div>



# ARSO Potresi - Home Assistant Custom Component

[![Python][python-shield]][python]
[![License][license-shield]][license]
[![Maintainer][maintainer-shield]][maintainer]
[![Home Assistant][homeassistant-shield]][homeassistant]
[![HACS][hacs-shield]][hacs]
[![GitHub Release](https://img.shields.io/github/v/release/andrejs2/arso_potresi?style=for-the-badge)](https://github.com/andrejs2/arso_potresi/releases/tag/v1.0.0)

![Made in Slovenia](https://img.shields.io/badge/Made_in-Slovenia-005DA4?style=for-the-badge&logo=flag&logoColor=white)  

[![BuyMeCoffee][buymecoffee-shield]][buymecoffee]
[![GitHub Sponsors][github-shield]][github]


[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrejs2&repository=arso_potresi&category=integration)


ARSO Potresi is a custom integration for [Home Assistant](https://www.home-assistant.io/) that fetches earthquake data from the ARSO Potresi API and presents it as a sensor entity. The sensor displays the most recent earthquake's location (e.g., "6 km JV od Jelšan") as its state, while additional details are available as attributes.

Data provided by ARSO Potresi - Agencija RS za okolje. This integration is unofficial.

## Features

- **Real-Time Earthquake Data:** Fetches the latest earthquake information from the ARSO Potresi API.
- **Sensor Entity:** Displays key data such as local and UTC times, location, coordinates, depth, magnitude, EMS-98 intensity, and verification status.
- **Device Registry Support:** The integration creates a device with proper device info and a unique ID.
- **Config Flow:** Configurable via Home Assistant’s UI, with a single option to set the update interval (in minutes).

## Installation

### HACS Button:
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrejs2&repository=arso_potresi&category=integration)

### Manual Installation

1. Place the integration folder in your Home Assistant `custom_components` directory:
   ```bash
   custom_components/arso_potresi/
   ├── __init__.py
   ├── const.py
   ├── config_flow.py
   └── sensor.py


2. Restart Home Assistant.

### Installation via HACS

If you use [HACS](https://hacs.xyz/), you can add this repository as a custom integration following the HACS documentation for custom integrations.

## Configuration

This integration is configured via the UI using Home Assistant's Config Flow. **No YAML configuration is required.**

1. Go to **Settings > Devices & Services > Integrations**.
2. Click **Add Integration** and search for **ARSO Potresi**.
3. In the configuration dialog, set the update interval (in minutes).
4. Complete the setup. The integration will create a sensor entity named `sensor.arso_potresi` that displays the most recent earthquake’s location as its state and includes all details as attributes.

## How It Works

- **Data Fetching:** The sensor fetches data from the ARSO Potresi API. It assumes that the first element in the returned JSON is the latest earthquake event.
- **Data Formatting:**  
- **Local Time:** Formatted from the API's `TIME` field (e.g., "20. 2. 2025 ob 23.11").
- **UTC Time:** Derived from the `TIME_ORIG` field.
- **Coordinates:** Latitude and longitude values are formatted with a comma as the decimal separator.
- **Additional Attributes:** Depth (with "km" appended), magnitude (formatted with one decimal and a comma), EMS-98 intensity (displayed as "-" if null), and verification status based on the `REVISION` field.

## Device Information

The sensor registers as a device in Home Assistant with the following information:

- **Identifiers:** `(arso_potresi, arso_potresi_sensor)`
- **Name:** ARSO Potresi
- **Manufacturer:** ARSO
- **Model:** Potresi

## Troubleshooting

- **Integration Not Showing Up:**  
- Ensure that the integration is placed in the correct directory: `custom_components/arso_potresi/`
- Check your Home Assistant logs for errors.
- Restart Home Assistant after installation.

- **Data Issues:**  
- Check the logs for any error messages during data fetch.


## Contributing

Contributions are welcome! 

## License

This project is licensed under the [MIT License](LICENSE).



[python-shield]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[python]: https://www.python.org/
[releases-shield]: https://img.shields.io/github/v/release/andrejs2/arso_potresi?style=for-the-badge
[releases]: https://github.com/andrejs2/arso_potresi/releases
[license-shield]: https://img.shields.io/github/license/andrejs2/arso_potresi?style=for-the-badge
[license]: ./LICENSE
[maintainer-shield]: https://img.shields.io/badge/MAINTAINER-%40andrejs2-41BDF5?style=for-the-badge
[maintainer]: https://github.com/andrejs2
[homeassistant-shield]: https://img.shields.io/badge/home%20assistant-%2341BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white
[homeassistant]: https://www.home-assistant.io/
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[hacs]: https://hacs.xyz/
[buymecoffee-shield]: https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black
[buymecoffee]: https://www.buymeacoffee.com/andrejs2
[github-shield]: https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA
[github]: https://github.com/sponsors/andrejs2
