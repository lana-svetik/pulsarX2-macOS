#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/controllers/performance.py
# Performance-Controller für Pulsar X2
# Updated 2025-04-17

"""
Performance-Controller für Pulsar X2.
Spezialisierte Funktionen für die Verwaltung der Performance-Optionen.
"""

from typing import Dict, Any, List
from ..config.settings import CMD_SET_MOTION_SYNC, CMD_SET_LIFTOFF, LIFT_OFF_DISTANCE

def create_motion_sync_command(enabled: bool) -> List[int]:
    """
    Erstellt einen Befehl zum Setzen von Motion Sync
    
    Args:
        enabled: Ob Motion Sync aktiviert werden soll
        
    Returns:
        List[int]: Befehlsbytes
    """
    command = CMD_SET_MOTION_SYNC.copy()
    command[1] = 1 if enabled else 0
    
    return command

def create_liftoff_command(distance: float) -> List[int]:
    """
    Erstellt einen Befehl zum Setzen der Lift-Off-Distanz
    
    Args:
        distance: Distanz in mm (0.7, 1.0, 2.0)
        
    Returns:
        List[int]: Befehlsbytes
    """
    # Gültigkeit der Distanz prüfen
    if distance not in LIFT_OFF_DISTANCE:
        closest_dist = min(LIFT_OFF_DISTANCE, key=lambda x: abs(x - distance))
        distance = closest_dist
    
    # Wert für das Protokoll ermitteln
    dist_values = {0.7: 0, 1.0: 1, 2.0: 2}
    dist_value = dist_values[distance]
    
    # Befehl zusammenstellen
    command = CMD_SET_LIFTOFF.copy()
    command[1] = dist_value
    
    return command

def get_performance_settings(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ermittelt die aktuellen Performance-Einstellungen aus der Konfiguration
    
    Args:
        config: Konfigurationsstruktur
        
    Returns:
        Dict[str, Any]: Performance-Einstellungen
    """
    active_profile = config["active_profile"]
    profile_config = config["profiles"][active_profile]
    
    return {
        "motion_sync": profile_config["motion_sync"],
        "ripple_control": profile_config.get("ripple_control", False),
        "angle_snap": profile_config.get("angle_snap", False),
        "debounce_time": profile_config.get("debounce_time", 3),
        "liftoff_distance": profile_config["liftoff_distance"]
    }
