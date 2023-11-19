# decode5
Dekodierer von 5-Ton-Folgen und Sirenensignalen

---
## Voraussetzungen
- Windows als Betriebssystem
- Python3 installiert

## Installation
- Starten der install_requirements.bat um die erforderlichen Libraries zu installieren
- Starten der start.bat

## Funktionsweise
Das Programm erkennt automatisch die jeweilige 5-Ton-Folge und das Sirenensignal und gibt es anschließend in der Konsole aus

## Sonderbefehle
### python index.py --devices
Gibt eine Übersicht der abgeschlossenen Audio-Geräte.
Es muss zwingend ein Input-Gerät ausgewählt werden. (Am Ende muss 1 in oder 2 in stehen)

## Credit / Lizens
Folgende Lizens wird angewandt: https://creativecommons.org/licenses/by-sa/3.0/deed.en#

Ein besonderer Dank gebührt @mboehn (https://github.com/mboehn/py5mon) für die Erstellung der Grund-Funktionalität.
Die grundlegende Audio-Erkennung wurde fast nicht verändert.
Aber es wurden einige Funktionalitäten hinzugefügt, beispielsweise die Erkennung des Sirenensignals.
