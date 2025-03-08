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

**ARSO Potresi** je prilagojena (custom) integracija za [Home Assistant](https://www.home-assistant.io/), ki pridobiva podatke o potresih iz ARSO Potresi API in jih prikazuje kot entiteto tipa senzor. Senzor prikaže zadnji zaznani potres (npr. »6 km JV od Jelšan«) v svojem stanju (state), dodatne informacije pa so na voljo v atributih.

Podatke zagotavlja ARSO Potresi - Agencija RS za okolje.

---

## Lastnosti

- **Pridobivanje podatkov v realnem času**: Integracija pridobi podatke o najnovejšem potresu neposredno iz ARSO Potresi API.
- **Senzorska entiteta**: Prikazuje ključno statistiko, kot so lokalni in UTC čas potresa, lokacija, koordinate, globina, magnituda, intenziteta (EMS-98) in status preverjenosti.
- **Podpora Device Registry**: Integracija ustvari napravo z ustreznimi informacijami in unikatnim ID-jem.
- **Config Flow**: Integracijo lahko enostavno namestite in urejate prek Home Assistant UI. Edina možnost konfiguracije je interval osveževanja v minutah.

---

## Namestitev

### HACS gumb:
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=andrejs2&repository=arso_potresi&category=integration)

### Ročna namestitev

1. V mapi `custom_components` vaše Home Assistant namestitve ustvarite mapo `arso_potresi` in vanjo namestite datoteke integracije:

   ```bash
   custom_components/arso_potresi/
   ├── __init__.py
   ├── const.py
   ├── config_flow.py
   └── sensor.py

   
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
