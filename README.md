[![latest version](https://img.shields.io/github/tag/thomas-svrts/hacs_blossom_app?include_prereleases=&sort=semver&label=Versie)](https://github.com/thomas-svrts/hacs_blossom_app/releases/)

# Blossom Energy Belgium Custom Component voor Home Assistant
Middels deze integratie wordt de informatie van Blossom gemaakt binnen Home Assistant.


## Installatie
Plaats de map `blossom_be` uit de map `custom_components` binnen deze repo in de `custom_components` map van je Home Assistant installatie.

### HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Installatie via HACS is mogelijk door deze repository toe te voegen als [custom repository](https://hacs.xyz/docs/faq/custom_repositories) met de categorie 'Integratie'.

### Configuratie

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=blossom_be" class="my badge" target="_blank">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg">
</a>

De Blossom integratie kan worden toegevoegd via de 'Integraties' pagina in de instellingen.
Vervolgens kunnen sensoren per stuk worden uitgeschakeld of verborgen indien gewenst.

#### Inloggen

Bij het instellen van de integratie moet je je refresh token van Blossom invoeren. Je kan dit vinden door in te loggen in de webversie app.blossom.be en via de debugger tools het token te achterhalen.
Dit wordt als response gevgeven op de request naar https://blossom-production.eu.auth0.com/oauth/token . Het refresh_token begint met v1.

### Gebruik
