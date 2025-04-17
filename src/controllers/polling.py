#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/controllers/polling.py
# Polling-Rate-Controller für Pulsar X2
# Updated 2025-04-17

"""
Polling-Rate-Controller für Pulsar X2.
Spezialisierte Funktionen für die Verwaltung der Polling-Rate.
"""

from typing import Dict, Any, List
from src.config.settings import CMD_SET_POLLING, POLLING_RATES

def create_polling_rate_command(rate: int) -> List[int]:
    """
    Erstellt einen Befehl zum Setzen der Polling-Rate
    
    Args:
        rate: Rate in Hz (125, 250, 500, 1000, 2000, 4000, 8000)
        
    Returns:
        List[int]: Befehlsbytes
    """
    # Gültigkeit der Rate prüfen
    if rate not in POLLING_RATES:
        closest_rate = min(POLLING_RATES, key=lambda x: abs(x - rate))
        rate = closest_rate
    
    # Wert für das Protokoll ermitteln
    rate_values = {
        125: 0,
        250: 1,
        500: 2,
        1000: 3,
        2000: 4,
        4000: 5,
        8000: 6
    }
    rate_value = rate_values[rate]
    
    # Befehl zusammenstellen
    command = CMD_SET_POLLING.copy()
    command[1] = rate_value
    
    return command

def get_polling_rate_from_config(config: Dict[str, Any]) -> int:
    """
    Ermittelt die aktuelle Polling-Rate aus der Konfiguration
    
    Args:
        config: Konfigurationsstruktur
        
    Returns:
        int: Polling-Rate in Hz
    """
    active_profile = config["active_profile"]
    profile_config = config["profiles"][active_profile]
    
    return profile_config["polling_rate"]

def requires_special_dongle(rate: int) -> bool:
    """
    Prüft, ob eine Polling-Rate einen speziellen 4K- oder 8K-Dongle erfordert
    
    Args:
        rate: Polling-Rate in Hz
        
    Returns:
        bool: True, wenn ein spezieller Dongle erforderlich ist
    """
    return rate > 1000
