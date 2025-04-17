#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/controllers/power.py
# Energiespar-Controller für Pulsar X2
# Updated 2025-04-17

"""
Energiespar-Controller für Pulsar X2.
Spezialisierte Funktionen für die Verwaltung der Energiesparoptionen.
"""

from typing import Dict, Any, List, Optional
from src.config.settings import CMD_SET_POWER

def create_power_saving_command(idle_time: int, low_battery_threshold: Optional[int] = None) -> List[int]:
    """
    Erstellt einen Befehl zum Setzen der Energiesparoptionen
    
    Args:
        idle_time: Zeit in Sekunden, bevor die Maus in den Ruhemodus wechselt (30-900)
        low_battery_threshold: Optionaler Prozentwert für den Low-Battery-Modus (5-20)
        
    Returns:
        List[int]: Befehlsbytes
    """
    # Gültigkeit der Werte prüfen
    idle_time = max(30, min(900, idle_time))
    
    # Befehl zusammenstellen
    command = CMD_SET_POWER.copy()
    command[1] = idle_time & 0xFF         # Low-Byte
    command[2] = (idle_time >> 8) & 0xFF  # High-Byte
    
    if low_battery_threshold is not None:
        low_battery_threshold = max(5, min(20, low_battery_threshold))
        command[3] = low_battery_threshold
    
    return command

def get_power_settings(config: Dict[str, Any]) -> Dict[str, int]:
    """
    Ermittelt die aktuellen Energiespareinstellungen aus der Konfiguration
    
    Args:
        config: Konfigurationsstruktur
        
    Returns:
        Dict[str, int]: Energiespareinstellungen
    """
    active_profile = config["active_profile"]
    power_config = config["profiles"][active_profile]["power_saving"]
    
    return {
        "idle_time": power_config["idle_time"],
        "low_battery_threshold": power_config["low_battery_threshold"]
    }

def is_wireless_mode(config: Dict[str, Any]) -> bool:
    """
    Prüft, ob die Maus im Wireless-Modus betrieben wird
    
    Args:
        config: Konfigurationsstruktur
        
    Returns:
        bool: True, wenn im Wireless-Modus
    """
    # Dies müsste tatsächlich aus der Hardware-Erkennung kommen,
    # ist aber hier als Platzhalter für Demonstrationszwecke
    return True
