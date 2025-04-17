#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/ui/cli.py
# Hilfsfunktionen für die Kommandozeilen-Schnittstelle
# Updated 2025-04-17

"""
Hilfsfunktionen für das macOS-CLI für Pulsar X2.
Vereinfacht die Ausgabe und Formatierung von Informationen in der Konsole.
"""

import os
import sys
from typing import Dict, Any, List, Optional

def clear_screen():
    """Bildschirm löschen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """
    Gibt eine Überschrift formatiert aus
    
    Args:
        title: Titel der Überschrift
    """
    width = min(os.get_terminal_size().columns, 80)
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)

def print_subheader(title: str):
    """
    Gibt eine Unterüberschrift formatiert aus
    
    Args:
        title: Titel der Unterüberschrift
    """
    width = min(os.get_terminal_size().columns, 80)
    print("\n" + "-" * width)
    print(title)
    print("-" * width)

def print_section(title: str):
    """
    Gibt einen Abschnittstitel formatiert aus
    
    Args:
        title: Titel des Abschnitts
    """
    print(f"\n--- {title} ---")

def print_menu(options: List[str], prompt: str = "Wählen Sie eine Option") -> str:
    """
    Gibt ein Menü aus und fordert zur Auswahl auf
    
    Args:
        options: Liste der Menüoptionen
        prompt: Aufforderungstext
        
    Returns:
        str: Ausgewählte Option
    """
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    if "0. Zurück" not in options and "0. Beenden" not in options:
        print("0. Zurück")
    
    return input(f"\n{prompt} (0-{len(options)}): ")

def print_value_list(items: Dict[str, Any], title: Optional[str] = None):
    """
    Gibt eine Liste von Werten mit Beschreibung aus
    
    Args:
        items: Dictionary mit Beschreibungen als Schlüssel und Werten
        title: Optionaler Titel
    """
    if title:
        print(f"\n{title}:")
    
    # Längste Beschreibung finden
    max_key_len = max(len(str(key)) for key in items.keys())
    
    for key, value in items.items():
        print(f"  {str(key):<{max_key_len}} : {value}")

def print_table(headers: List[str], rows: List[List[Any]]):
    """
    Gibt eine Tabelle formatiert aus
    
    Args:
        headers: Spaltentitel
        rows: Zeilen mit Werten
    """
    if not rows:
        print("Keine Daten vorhanden.")
        return
    
    # Spaltenbreiten berechnen
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Kopfzeile ausgeben
    header_row = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_row)
    print("-" * len(header_row))
    
    # Datenzeilen ausgeben
    for row in rows:
        row_str = " | ".join(f"{str(cell):<{w}}" for cell, w in zip(row, col_widths))
        print(row_str)

def confirm_action(prompt: str = "Möchten Sie fortfahren?") -> bool:
    """
    Fordert eine Bestätigung vom Benutzer an
    
    Args:
        prompt: Aufforderungstext
        
    Returns:
        bool: True, wenn der Benutzer bestätigt hat, sonst False
    """
    response = input(f"{prompt} (j/n): ").lower()
    return response in ("j", "ja", "y", "yes")

def input_int(prompt: str, min_value: int, max_value: int) -> Optional[int]:
    """
    Fordert eine Ganzzahl vom Benutzer an
    
    Args:
        prompt: Aufforderungstext
        min_value: Minimaler Wert
        max_value: Maximaler Wert
        
    Returns:
        int: Eingegebene Zahl oder None bei Abbruch
    """
    value = input(f"{prompt} ({min_value}-{max_value}): ")
    
    if not value:
        return None
        
    try:
        int_value = int(value)
        if min_value <= int_value <= max_value:
            return int_value
        else:
            print(f"Wert muss zwischen {min_value} und {max_value} liegen.")
            return None
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        return None

def input_float(prompt: str, min_value: float, max_value: float) -> Optional[float]:
    """
    Fordert eine Fließkommazahl vom Benutzer an
    
    Args:
        prompt: Aufforderungstext
        min_value: Minimaler Wert
        max_value: Maximaler Wert
        
    Returns:
        float: Eingegebene Zahl oder None bei Abbruch
    """
    value = input(f"{prompt} ({min_value}-{max_value}): ")
    
    if not value:
        return None
        
    try:
        float_value = float(value)
        if min_value <= float_value <= max_value:
            return float_value
        else:
            print(f"Wert muss zwischen {min_value} und {max_value} liegen.")
            return None
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        return None

def input_choice(prompt: str, choices: List[Any]) -> Optional[Any]:
    """
    Fordert eine Auswahl aus einer Liste vom Benutzer an
    
    Args:
        prompt: Aufforderungstext
        choices: Liste der möglichen Auswahlmöglichkeiten
        
    Returns:
        Any: Ausgewählter Wert oder None bei Abbruch
    """
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    
    value = input(f"{prompt} (1-{len(choices)}): ")
    
    if not value:
        return None
        
    try:
        int_value = int(value)
        if 1 <= int_value <= len(choices):
            return choices[int_value - 1]
        else:
            print(f"Bitte eine Zahl zwischen 1 und {len(choices)} eingeben.")
            return None
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
        return None
