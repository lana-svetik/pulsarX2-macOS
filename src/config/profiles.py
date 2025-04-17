#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/config/profiles.py
# Funktionen zur Verwaltung von Profilen für Pulsar X2
# Updated 2025-04-17
"""
Funktionen zur Verwaltung von Profilen für Pulsar X2.
Bietet Funktionen zum Laden, Speichern und Erstellen von Konfigurationsprofilen.
"""

import os
import json
from typing import Dict, Any

from .settings import CONFIG_DIR, CONFIG_FILE

def ensure_config_dir() -> bool:
    """
    Stellt sicher, dass das Konfigurationsverzeichnis existiert
    
    Returns:
        bool: True, wenn das Verzeichnis existiert oder erstellt wurde, sonst False
    """
    if not os.path.exists(CONFIG_DIR):
        try:
            os.makedirs(CONFIG_DIR)
            print(f"Konfigurationsverzeichnis erstellt: {CONFIG_DIR}")
        except Exception as e:
            print(f"Fehler beim Erstellen des Konfigurationsverzeichnisses: {e}")
            return False
    return True

def save_config(config: Dict[str, Any]) -> bool:
    """
    Speichert die Konfiguration in eine Datei
    
    Args:
        config: Konfigurationsdaten als Dictionary
        
    Returns:
        bool: True bei Erfolg, sonst False
    """
    if not ensure_config_dir():
        return False
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Konfiguration gespeichert: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {e}")
        return False

def load_config() -> Dict[str, Any]:
    """
    Lädt die Konfiguration aus einer Datei
    
    Returns:
        Dict[str, Any]: Geladene Konfiguration oder Standardkonfiguration bei Fehler
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"Keine gespeicherte Konfiguration gefunden, verwende Standardwerte.")
        return create_default_config()
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"Konfiguration geladen: {CONFIG_FILE}")
        return config
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        return create_default_config()

def create_default_config() -> Dict[str, Any]:
    """
    Erstellt eine Standardkonfiguration
    
    Returns:
        Dict[str, Any]: Standardkonfiguration
    """
    return {
        "profiles": {
            "1": {
                "dpi_stages": {
                    "1": 800,
                    "2": 1600,
                    "3": 3200,
                    "4": 6400,
                    "5": 12800,
                    "6": 25600
                },
                "active_dpi_stage": 2,  # Standardmäßig Stufe 2 (1600 DPI)
                "polling_rate": 1000,
                "liftoff_distance": 1.0,
                "buttons": {
                    "1": {"action": "Linksklick", "code": 0x01},
                    "2": {"action": "Rechtsklick", "code": 0x02},
                    "3": {"action": "Mittlere Taste", "code": 0x03},
                    "4": {"action": "Zurück", "code": 0x04},
                    "5": {"action": "Vorwärts", "code": 0x05}
                },
                "motion_sync": True,
                "ripple_control": False,
                "angle_snap": False,
                "debounce_time": 3,
                "power_saving": {
                    "idle_time": 30,  # Sekunden
                    "low_battery_threshold": 10  # Prozent
                }
            }
        },
        "active_profile": "1"
    }

def print_profile_settings(config: Dict[str, Any], profile_id: str = None) -> None:
    """
    Gibt die Einstellungen eines Profils formatiert aus
    
    Args:
        config: Konfigurationsstruktur
        profile_id: Profil-ID, falls None wird das aktive Profil verwendet
    """
    active_profile = profile_id or config["active_profile"]
    if active_profile not in config["profiles"]:
        print(f"Fehler: Profil {active_profile} nicht gefunden.")
        return
        
    profile_config = config["profiles"][active_profile]
    
    print("\n=== Profileinstellungen ===")
    print(f"Profil: {active_profile}" + (" (aktiv)" if active_profile == config["active_profile"] else ""))
    
    # DPI-Einstellungen
    print("\nDPI-Stufen:")
    for stage, dpi in profile_config["dpi_stages"].items():
        marker = " *" if int(stage) == profile_config["active_dpi_stage"] else ""
        print(f"  Stufe {stage}: {dpi} DPI{marker}")
    
    # Polling-Rate
    print(f"\nPolling-Rate: {profile_config['polling_rate']} Hz")
    
    # Lift-Off-Distanz
    print(f"Lift-Off-Distanz: {profile_config['liftoff_distance']} mm")
    
    # Tastenbelegung
    print("\nTastenbelegung:")
    for button, config in profile_config["buttons"].items():
        print(f"  Taste {button}: {config['action']} (Code: 0x{config['code']:02x})")
    
    # Weitere Einstellungen
    print("\nWeitere Einstellungen:")
    print(f"  Motion Sync: {'Ein' if profile_config['motion_sync'] else 'Aus'}")
    print(f"  Ripple Control: {'Ein' if profile_config.get('ripple_control', False) else 'Aus'}")
    print(f"  Angle Snap: {'Ein' if profile_config.get('angle_snap', False) else 'Aus'}")
    print(f"  Debounce-Zeit: {profile_config.get('debounce_time', 3)} ms")
    
    # Energiesparoptionen
    print("\nEnergiesparoptionen:")
    print(f"  Idle-Zeit: {profile_config['power_saving']['idle_time']} Sekunden")
    print(f"  Low-Battery-Schwellwert: {profile_config['power_saving']['low_battery_threshold']}%")

def copy_profile(config: Dict[str, Any], source_id: str, target_id: str) -> Dict[str, Any]:
    """
    Kopiert ein Profil
    
    Args:
        config: Konfigurationsstruktur
        source_id: Quellprofil-ID
        target_id: Zielprofil-ID
        
    Returns:
        Dict[str, Any]: Aktualisierte Konfiguration
    """
    if source_id not in config["profiles"]:
        print(f"Fehler: Quellprofil {source_id} nicht gefunden.")
        return config
        
    # Profil kopieren
    config["profiles"][target_id] = config["profiles"][source_id].copy()
    print(f"Profil {source_id} wurde nach Profil {target_id} kopiert.")
    
    return config

def reset_profile(config: Dict[str, Any], profile_id: str) -> Dict[str, Any]:
    """
    Setzt ein Profil auf Standardwerte zurück
    
    Args:
        config: Konfigurationsstruktur
        profile_id: Profil-ID
        
    Returns:
        Dict[str, Any]: Aktualisierte Konfiguration
    """
    default_config = create_default_config()
    
    if profile_id not in config["profiles"]:
        print(f"Fehler: Profil {profile_id} nicht gefunden.")
        return config
        
    # Profil zurücksetzen
    config["profiles"][profile_id] = default_config["profiles"]["1"].copy()
    print(f"Profil {profile_id} wurde auf Standardwerte zurückgesetzt.")
    
    return config
