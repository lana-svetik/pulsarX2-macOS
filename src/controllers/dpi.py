#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/controllers/dpi.py
# DPI-Controller für Pulsar X2
# Updated 2025-04-17
"""
DPI-Controller für Pulsar X2.
Spezialisierte Funktionen für die Verwaltung der DPI-Einstellungen.
"""

from typing import Dict, Any, List, Optional
from ..config.settings import CMD_SET_DPI, MAX_DPI

def create_dpi_command(dpi: int, stage: int = 1) -> List[int]:
    """
    Erstellt einen Befehl zum Setzen der DPI
    
    Args:
        dpi: DPI-Wert (50-32000)
        stage: DPI-Stufe (1-6)
        
    Returns:
        List[int]: Befehlsbytes
    """
    # DPI-Wert auf gültigen Bereich beschränken und auf 10er-Schritte runden
    dpi = max(50, min(MAX_DPI, dpi))
    dpi = round(dpi / 10) * 10
    
    # Befehl zusammenstellen
    command = CMD_SET_DPI.copy()
    command[1] = stage
    command[2] = (dpi >> 8) & 0xFF  # High-Byte
    command[3] = dpi & 0xFF         # Low-Byte
    
    return command

def get_dpi_from_config(config: Dict[str, Any], stage: Optional[int] = None) -> int:
    """
    Ermittelt den aktuellen DPI-Wert aus der Konfiguration
    
    Args:
        config: Konfigurationsstruktur
        stage: Optional, DPI-Stufe (1-6). Wenn None, wird die aktive Stufe verwendet
        
    Returns:
        int: DPI-Wert
    """
    active_profile = config["active_profile"]
    profile_config = config["profiles"][active_profile]
    
    if stage is None:
        stage = profile_config["active_dpi_stage"]
    
    return profile_config["dpi_stages"][str(stage)]

def set_active_dpi_stage(config: Dict[str, Any], stage: int) -> Dict[str, Any]:
    """
    Setzt die aktive DPI-Stufe in der Konfiguration
    
    Args:
        config: Konfigurationsstruktur
        stage: DPI-Stufe (1-6)
        
    Returns:
        Dict[str, Any]: Aktualisierte Konfiguration
    """
    if not 1 <= stage <= 6:
        raise ValueError(f"Ungültige DPI-Stufe: {stage}. Gültige Werte sind 1-6.")
    
    active_profile = config["active_profile"]
    config["profiles"][active_profile]["active_dpi_stage"] = stage
    
    return config

def cycle_dpi_stage(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wechselt zur nächsten DPI-Stufe
    
    Args:
        config: Konfigurationsstruktur
        
    Returns:
        Dict[str, Any]: Aktualisierte Konfiguration
    """
    active_profile = config["active_profile"]
    profile_config = config["profiles"][active_profile]
    current_stage = profile_config["active_dpi_stage"]
    
    # Anzahl der konfigurierten Stufen ermitteln
    stages = sorted([int(s) for s in profile_config["dpi_stages"].keys()])
    max_stage = max(stages)
    
    # Zur nächsten Stufe wechseln oder zum Anfang zurückkehren
    next_stage = current_stage + 1 if current_stage < max_stage else 1
    
    # Aktive Stufe aktualisieren
    profile_config["active_dpi_stage"] = next_stage
    
    return config
