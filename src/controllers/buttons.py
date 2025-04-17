#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/controllers/buttons.py
# Button-Controller für Pulsar X2
# Updated 2025-04-17

"""
Button-Controller für Pulsar X2.
Spezialisierte Funktionen für die Verwaltung der Tastenbelegung.
"""

from typing import Dict, Any, List, Optional
from src.config.settings import CMD_SET_BUTTON, BUTTON_ACTIONS

def create_button_command(button: int, action_name: str) -> Optional[List[int]]:
    """
    Erstellt einen Befehl zum Setzen der Tastenbelegung
    
    Args:
        button: Tastennummer (1-5)
        action_name: Name der Aktion aus BUTTON_ACTIONS
        
    Returns:
        Optional[List[int]]: Befehlsbytes oder None bei Fehler
    """
    # Gültigkeit der Taste prüfen
    if not 1 <= button <= 5:
        return None
    
    # Gültigkeit der Aktion prüfen
    if action_name not in BUTTON_ACTIONS:
        return None
    
    action_code = BUTTON_ACTIONS[action_name]
    
    # Befehl zusammenstellen
    command = CMD_SET_BUTTON.copy()
    command[1] = button
    command[2] = action_code
    
    return command

def get_button_config(config: Dict[str, Any], button: int) -> Optional[Dict[str, Any]]:
    """
    Ermittelt die aktuelle Konfiguration einer Taste
    
    Args:
        config: Konfigurationsstruktur
        button: Tastennummer (1-5)
        
    Returns:
        Optional[Dict[str, Any]]: Tastenkonfiguration oder None bei Fehler
    """
    if not 1 <= button <= 5:
        return None
    
    active_profile = config["active_profile"]
    profile_config = config["profiles"][active_profile]
    
    return profile_config["buttons"].get(str(button))

def get_action_name(action_code: int) -> Optional[str]:
    """
    Ermittelt den Namen einer Aktion anhand des Codes
    
    Args:
        action_code: Aktionscode
        
    Returns:
        Optional[str]: Aktionsname oder None, wenn nicht gefunden
    """
    for name, code in BUTTON_ACTIONS.items():
        if code == action_code:
            return name
    
    return None
