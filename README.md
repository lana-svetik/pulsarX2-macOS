# macOS-CLI für Pulsar X2

Ein Kommandozeilentool zur Konfiguration der Gaming-Maus Pulsar X2 unter macOS. Erstellt unter Anleitung von Claude 3.7 Sonnet.

## Beschreibung

Da die offizielle Pulsar-Software nur für Windows verfügbar ist, ermöglicht dieses Tool die vollständige Konfiguration der unter macOS. Es bietet Zugriff auf alle wichtigen Funktionen der Maus wie DPI-Einstellungen, Polling-Rate, Lift-Off-Distanz (LOD), Tastenbelegung und Energiesparoptionen.

## Funktionen

- Vollständige Kontrolle über die Mauseinstellungen unter macOS
- Einstellung der DPI (50-32000)
- Anpassung der Polling-Rate (125-8000 Hz)
- Einstellung der Lift-Off-Distanz (0.7, 1.0, 2.0 mm)
- Vollständige Tastenkonfiguration
- Motion Sync und andere Performanceoptionen
- Energiesparoptionen für den kabellosen Betrieb
- Speichern und Laden von Profilen
- Diagnostiktool für Reverse Engineering

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- macOS 10.15 oder höher
- Root-Rechte für USB-Zugriff (`sudo`)

### Installation über pip

```bash
pip install git+https://github.com/lana-svetik/pulsarX2-macOS.git
```

### Installation aus dem Quellcode

```bash
git clone https://github.com/lana-svetik/pulsarX2-macOS.git
cd pulsarX2-macOS.git
pip install -e .
```

## Verwendung

### Interaktiver Modus

```bash
sudo pulsarX2-macOS
```

### Kommandozeilenparameter

```bash
# DPI und Stufe setzen
sudo pulsarX2-macOS --dpi 1600 --stage 1

# Polling-Rate ändern
sudo pulsarX2-macOS --polling 1000

# Lift-Off-Distanz einstellen
sudo pulsarX2-macOS --liftoff 1.0

# Motion Sync ein- oder ausschalten
sudo pulsarX2-macOS --motion-sync on

# Energiesparoptionen konfigurieren
sudo pulsarX2-macOS --idle-time 60 --battery-threshold 10

# Aktuelle Einstellungen anzeigen
sudo pulsarX2-macOS --settings

# Debug-Modus (ohne tatsächliche USB-Kommunikation)
sudo pulsarX2-macOS --debug
```

### USB-Monitor für Reverse-Engineering

```bash
# USB-Verkehr überwachen und in eine Datei schreiben
sudo pulsar-usb-monitor --monitor --duration 60 --log usb_log.txt

# Protokolldatei analysieren
sudo pulsar-usb-monitor --analyze usb_log.txt

# Spezifischen Befehl senden
sudo pulsar-usb-monitor --command "20 01 04 B0 00 00 00"
```

## Architektur

Das Projekt ist modular aufgebaut und besteht aus den folgenden Komponenten:

- **USB-Kommunikation**: Implementiert in `src/usb/usb_protocol.py` und `src/usb/usb_monitor.py`
- **Konfigurationsverwaltung**: Implementiert in `src/config/settings.py` und `src/config/profiles.py`
- **Controller**: Spezifische Funktionen für DPI, Polling-Rate, Tasten usw. in `src/controllers/`
- **Benutzeroberfläche**: CLI und interaktive Schnittstelle in `src/ui/`

## Hinweise

- Das Tool muss mit Root-Rechten ausgeführt werden, um auf die USB-Schnittstelle zugreifen zu können.
- Die Polling-Raten über 1000Hz erfordern einen speziellen 4K/8K-Dongle (Produkt-ID: 0x5406 statt 0x5402).
- Die USB-Kommunikationsprotokolle wurden durch Reverse-Engineering ermittelt und könnten sich mit Firmware-Updates ändern.
- Bei Problemen empfiehlt es sich, zunächst den USB-Monitor zu verwenden, um die Kommunikation zwischen der Windows-Software und der Maus zu analysieren.

## Bekannte Probleme

- Einige fortgeschrittene Funktionen wie Ripple Control und Angle Snap sind noch nicht vollständig implementiert.
- Bei einigen macOS-Versionen können Probleme mit dem Kernel-Treiber auftreten. Versuchen Sie in diesem Fall, das Tool mit dem `--debug`-Parameter zu starten und die Ausgabe zu analysieren.

## Fehlerbehebung

1. **Maus wird nicht erkannt**: Stellen Sie sicher, dass die Maus angeschlossen ist und die richtigen USB-IDs hat (Vendor ID: `0x3710`, Product ID: `0x5402` für 1K oder `0x5406` für 8K-Dongle).
2. **Keine Änderung der Einstellungen**: Prüfen Sie, ob das Tool mit Root-Rechten ausgeführt wird (`sudo`).
3. **USB-Fehler**: Verwenden Sie den USB-Monitor, um die Kommunikation zu debuggen und Probleme zu identifizieren.
4. **Berechtigungsprobleme auf neueren macOS-Versionen**: 
   - Seit macOS 10.15 (Catalina) benötigen USB-Geräte spezielle Berechtigungen.
   - Navigieren Sie zu `Systemeinstellungen > Sicherheit & Datenschutz > Privatsphäre > Eingabehilfen` und fügen Sie `Terminal` hinzu.
   - Bei der ersten Verbindung könnte eine Berechtigungsanfrage erscheinen, die genehmigt werden muss.
5. **"Entity not found"**:
   - Dies deutet auf ein Berechtigungsproblem hin. Führen Sie das Tool mit `sudo` aus.
   - Wenn das Problem bestehen bleibt, starten Sie Ihren Mac neu und versuchen Sie es erneut.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
