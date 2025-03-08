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
2. Ponovno zaženite Home Assistant.

### Namestitev prek HACS

Če uporabljate [HACS](https://hacs.xyz/), lahko ta repozitorij dodate kot **custom integration** po navodilih HACS za integracije po meri.

## Konfiguracija

Ta integracija se nastavi prek uporabniškega vmesnika (Config Flow). **YAML konfiguracija ni potrebna.**

1. Pojdite v **Nastavitve > Naprave in storitve > Integrations**.
2. Kliknite **Dodaj integracijo (Add Integration)** in poiščite **ARSO Potresi**.
3. V pogovornem oknu konfiguracije nastavite interval osveževanja (v minutah).
4. Dokončajte namestitev. Integracija bo ustvarila senzor z imenom `sensor.arso_potresi`, ki prikazuje lokacijo zadnjega zaznanega potresa kot svoje stanje, vse dodatne podrobnosti pa so na voljo v atributih.

## Kako deluje

- **Pridobivanje podatkov**: Senzor pridobi podatke iz ARSO Potresi API. Predvideva, da je prvi element v JSON-odgovoru najnovejši potres.
- **Oblikovanje podatkov**:  
  - **Lokalni čas**: Formatiran iz polja `TIME` (npr. »20. 2. 2025 ob 23.11«).
  - **UTC čas**: Odvzet iz polja `TIME_ORIG`.
  - **Koordinate**: Zemljepisna širina in dolžina sta zapisani z vejico kot decimalnim ločilom.
  - **Dodatni atributi**: Globina (z besedo "km"), magnituda (z eno decimalko in vejico), intenziteta EMS-98 (prikazana kot "-" ob ničelni vrednosti) in status preverjenosti po polju `REVISION`.

## Informacije o napravi

Senzor se v Home Assistantu registrira kot naprava z naslednjimi podatki:

- **Identifiers:** `(arso_potresi, arso_potresi_sensor)`
- **Name:** ARSO Potresi
- **Manufacturer:** ARSO
- **Model:** Potresi

## Reševanje težav

- **Integracija se ne prikaže**:  
  - Preverite, da je integracija nameščena v pravilno mapo: `custom_components/arso_potresi/`
  - Preverite dnevnik (log) Home Assistanta za morebitne napake.
  - Po namestitvi ponovno zaženite Home Assistant.

- **Težave s podatki**:  
  - V dnevniku preverite morebitna sporočila o napakah pri pridobivanju podatkov.

## Prispevki

Prispevki so dobrodošli!

## Licenca

Ta projekt je licenciran pod [MIT licenco](LICENSE).

   
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
