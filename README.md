[![latest version](https://img.shields.io/github/tag/thomas-svrts/hacs_blossom_energy?include_prereleases=&sort=semver&label=Versie)](https://github.com/thomas-svrts/hacs_blossom_energy/releases/)

# Blossom.be Custom Component voor Home Assistant
Met deze integratie wordt de informatie van Blossom.be beschikbaar gemaakt binnen Home Assistant.

## Installatie
Implement translations

## Installatie
Plaats de map `blossom_be` uit de map `custom_components` binnen deze repo in de `custom_components` map van je Home Assistant installatie.

### HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=thomas-svrts&repository=blossom_be&category=Integration)

Installatie via HACS is mogelijk door deze repository toe te voegen als [custom repository](https://hacs.xyz/docs/faq/custom_repositories) met de categorie 'Integratie'.

### Configuratie

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=blossom_be" class="my badge" target="_blank">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg">
</a>

De Blossom integratie kan worden toegevoegd via de 'Integraties' pagina in de instellingen.
Vervolgens kunnen sensoren per stuk worden uitgeschakeld of verborgen indien gewenst.

#### Inloggen

Bij het instellen van de integratie moet je je refresh token van Blossom invoeren. Je kan dit vinden door in te loggen (in inPrivate window) in de webversie "app.blossom.be" en via de debugger tools het token te achterhalen.
Dit wordt als response gevgeven op de request naar https://blossom-production.eu.auth0.com/oauth/token . Het refresh_token begint met v1.

remarks: Wanneer je de refresh token hebt gekopieerd dien je je inPrivate te sluiten zonder af te melden van Blossom, zo blijft je dat refresh token verder 'leven'.
Wanneer je dit niet afsluit zal je browser een tijd later een nieuw refresh token aanvragen, en ook dan vervalt je oude token (Blossom hanteert [refresh token rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)).
![image](https://github.com/user-attachments/assets/ae586db1-ef7a-44b2-8b7e-2d99fa82f25f)


### Gebruik

Deze integratie kan bijvoorbeeld gebruikt worden om het energie verbruik van je laadpaal op te volgen en weer te geven in je energy dashboard (gebruik hierboor sensor.session_consumption, deze is near realtime.). Daarnaast gebruik ik het ook om de modus van mijn laadpaal automatisch te wisselen op basis van de huidige marktprijs. Wanneer de electriciteitsprijs daalt onder een threshold, schakelt mijn laadpaal over naar de standaard modus, bij dure prijzen naar Zon.

<img width="400" alt="Capture" src="https://github.com/user-attachments/assets/2b9a2f19-f5e2-4774-82fa-0ce5be89396f" />


![image](https://github.com/user-attachments/assets/0297f6a7-7824-4d7d-90fc-19dc8ed19bf3)
