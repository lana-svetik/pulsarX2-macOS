#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/config/settings.py
# Konstanten und Einstellungen für das macOS-CLI für Pulsar X2
# Updated 2025-04-17
"""
Konstanten und Einstellungen für Pulsar X2.
Enthält USB-IDs, DPI-Bereiche, Polling-Raten und weitere Konfigurationswerte.
"""

import os
from typing import Dict, List, Tuple, Any

# USB-IDs für die Pulsar X2 V3 Maus
VENDOR_ID = 0x3710  # Pulsar Vendor ID
PRODUCT_ID = 0x5402  # Produkt ID für 1K-Dongle; 0x5406 für 8K-Dongle

# Modellspezifikationen
MODEL_NAME = "X2"
SENSOR_MODEL = "XS-1 (PixArt)"
MAX_DPI = 32000
MAX_POLLING_RATE = 8000  # Mit speziellem Dongle

# Konfigurationswerte
DPI_RANGE = range(50, MAX_DPI + 50, 10)  # 50 bis 32000 in 10er-Schritten
DEFAULT_DPI_STAGES = [800, 1600, 3200, 6400, 12800, 25600]  # Standardwerte für 6 Stufen
POLLING_RATES = [125, 250, 500, 1000, 2000, 4000, 8000]  # Standard + 8K mit speziellem Dongle
LIFT_OFF_DISTANCE = [0.7, 1.0, 2.0]  # in mm

# Tastenkonfiguration
BUTTON_ACTIONS = {
    "Linksklick": 0x01,
    "Rechtsklick": 0x02,
    "Mittlere Taste": 0x03,
    "Zurück": 0x04,
    "Vorwärts": 0x05,
    "DPI Hoch": 0x06,
    "DPI Runter": 0x07,
    "DPI Zyklus": 0x08,
    "Scrollrad Hoch": 0x09,
    "Scrollrad Runter": 0x0A,
    "Doppelklick": 0x0B,
    "Strg": 0x10,
    "Shift": 0x11,
    "Alt": 0x12,
    "Windows/Command": 0x13,
    "Deaktiviert": 0x00
}

# Standardpfad für Konfigurationsdateien
CONFIG_DIR = os.path.expanduser("~/.config/pulsar")
CONFIG_FILE = os.path.join(CONFIG_DIR, "pulsar_x2_v3_config.json")

# USB-Kommunikationsprotokolle (hypothetisch - muss angepasst werden)
# Diese Befehlsstrukturen wurden nicht reverse-engineered und sind nur als Vorlage
# Die tatsächlichen Befehle müssen durch Reverse Engineering ermittelt werden

# Hypothetisches Befehlsformat: [Befehlstyp, Parameter1, Parameter2, ...]
CMD_GET_INFO =          [0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
CMD_GET_SETTINGS =      [0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
CMD_SET_DPI =           [0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Stage, DPI-Hi, DPI-Lo
CMD_SET_POLLING =       [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Rate
CMD_SET_LIFTOFF =       [0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Distanz
CMD_SET_BUTTON =        [0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Button, Aktion
CMD_SET_MOTION_SYNC =   [0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Status
CMD_SET_POWER =         [0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Zeit
CMD_SAVE_PROFILE =      [0xF0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]  # + Profil
