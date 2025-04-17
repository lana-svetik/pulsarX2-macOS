#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/ui/interactive.py
# Interaktive Kommandozeilenschnittstelle für das macOS-CLI für die Pulsar X2
# Updated 2025-04-17

"""
Interaktive Kommandozeilenschnittstelle für das macOS-CLI für die Pulsar X2.
Ermöglicht die Konfiguration der Maus über ein Menüsystem.
"""

from typing import Dict, Any, List

from ..config.settings import (MODEL_NAME, SENSOR_MODEL, MAX_DPI, MAX_POLLING_RATE,
                           DPI_RANGE, POLLING_RATES, LIFT_OFF_DISTANCE, BUTTON_ACTIONS)

def interactive_cli(mouse):
    """
    Interaktive Kommandozeilen-Schnittstelle für die Maus-Konfiguration
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n===== macOS-CLI für Pulsar X2 =====")
    print(f"Modell: {MODEL_NAME}")
    print(f"Sensor: {SENSOR_MODEL}")
    print("Version: 1.0.0")
    
    # Aktuelle Einstellungen anzeigen
    mouse.show_current_settings()
    
    while True:
        print("\nHauptmenü:")
        print("1. DPI-Einstellungen")
        print("2. Polling-Rate ändern")
        print("3. Lift-Off-Distanz ändern")
        print("4. Tastenbelegung ändern")
        print("5. Performance-Optionen")
        print("6. Energiesparoptionen")
        print("7. Geräteinformationen anzeigen")
        print("8. Aktuelle Einstellungen anzeigen")
        print("9. Einstellungen in Profil speichern")
        print("0. Beenden")
        
        choice = input("\nWählen Sie eine Option (0-9): ")
        
        if choice == "1":
            handle_dpi_settings(mouse)
        elif choice == "2":
            handle_polling_rate(mouse)
        elif choice == "3":
            handle_liftoff_distance(mouse)
        elif choice == "4":
            handle_button_mapping(mouse)
        elif choice == "5":
            handle_performance_options(mouse)
        elif choice == "6":
            handle_power_options(mouse)
        elif choice == "7":
            mouse.get_device_info()
        elif choice == "8":
            mouse.show_current_settings()
        elif choice == "9":
            handle_profile_saving(mouse)
        elif choice == "0":
            print("\nProgramm wird beendet...")
            break
        else:
            print("Ungültige Eingabe. Bitte eine Zahl zwischen 0 und 9 eingeben.")

def handle_dpi_settings(mouse):
    """
    Behandelt die DPI-Einstellungen im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- DPI-Einstellungen ---")
    active_profile = mouse.config["active_profile"]
    profile_config = mouse.config["profiles"][active_profile]
    
    # Aktuelle DPI-Stufen anzeigen
    print("Aktuelle DPI-Stufen:")
    for stage, dpi in profile_config["dpi_stages"].items():
        marker = " *" if int(stage) == profile_config["active_dpi_stage"] else ""
        print(f"  Stufe {stage}: {dpi} DPI{marker}")
    
    # Stufe auswählen
    stage = input("\nWelche Stufe möchten Sie ändern? (1-6): ")
    if not stage.isdigit() or not 1 <= int(stage) <= 6:
        print("Ungültige Eingabe. Bitte eine Zahl zwischen 1 und 6 eingeben.")
        return
    
    # DPI-Wert eingeben
    dpi = input(f"Neuer DPI-Wert für Stufe {stage} (50-{MAX_DPI}): ")
    if not dpi.isdigit() or not 50 <= int(dpi) <= MAX_DPI:
        print(f"Ungültiger DPI-Wert. Bitte einen Wert zwischen 50 und {MAX_DPI} eingeben.")
        return
    
    # DPI setzen
    mouse.set_dpi(int(dpi), int(stage))

def handle_polling_rate(mouse):
    """
    Behandelt die Polling-Rate im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Polling-Rate ändern ---")
    print("Verfügbare Polling-Rates:")
    for rate in POLLING_RATES:
        print(f"  {rate} Hz")
    print("Hinweis: Rates über 1000Hz erfordern einen speziellen 4K- oder 8K-Dongle.")
    
    rate = input("\nNeue Polling-Rate (125, 250, 500, 1000, 2000, 4000, 8000): ")
    if not rate.isdigit() or int(rate) not in POLLING_RATES:
        print("Ungültige Eingabe. Bitte eine der verfügbaren Polling-Rates eingeben.")
        return
    
    mouse.set_polling_rate(int(rate))

def handle_liftoff_distance(mouse):
    """
    Behandelt die Lift-Off-Distanz im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Lift-Off-Distanz ändern ---")
    print("Verfügbare Distanzen:")
    for dist in LIFT_OFF_DISTANCE:
        print(f"  {dist} mm")
    
    dist = input("\nNeue Lift-Off-Distanz (0.7, 1.0, 2.0): ")
    try:
        dist_float = float(dist)
        if dist_float not in LIFT_OFF_DISTANCE:
            print("Ungültige Eingabe. Bitte eine der verfügbaren Distanzen eingeben.")
            return
        
        mouse.set_liftoff_distance(dist_float)
    except ValueError:
        print("Ungültige Eingabe. Bitte eine gültige Zahl eingeben.")
        return

def handle_button_mapping(mouse):
    """
    Behandelt die Tastenbelegung im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Tastenbelegung ändern ---")
    print("Verfügbare Tasten:")
    print("  1: Linke Maustaste")
    print("  2: Rechte Maustaste")
    print("  3: Mittlere Taste / Mausrad")
    print("  4: Seitentaste Zurück")
    print("  5: Seitentaste Vorwärts")
    
    button = input("\nWelche Taste möchten Sie neu belegen? (1-5): ")
    if not button.isdigit() or not 1 <= int(button) <= 5:
        print("Ungültige Eingabe. Bitte eine Zahl zwischen 1 und 5 eingeben.")
        return
    
    print("\nVerfügbare Aktionen:")
    for i, (action, code) in enumerate(BUTTON_ACTIONS.items(), 1):
        print(f"  {i}: {action} (Code: 0x{code:02x})")
    
    action_choice = input("\nWählen Sie eine Aktion (1-{}): ".format(len(BUTTON_ACTIONS)))
    if not action_choice.isdigit() or not 1 <= int(action_choice) <= len(BUTTON_ACTIONS):
        print("Ungültige Eingabe. Bitte eine gültige Aktionsnummer eingeben.")
        return
    
    action_name = list(BUTTON_ACTIONS.keys())[int(action_choice) - 1]
    mouse.set_button_mapping(int(button), action_name)

def handle_performance_options(mouse):
    """
    Behandelt die Performance-Optionen im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Performance-Optionen ---")
    active_profile = mouse.config["active_profile"]
    profile_config = mouse.config["profiles"][active_profile]
    
    print("1. Motion Sync: {}".format("Ein" if profile_config["motion_sync"] else "Aus"))
    print("2. Ripple Control: {}".format("Ein" if profile_config.get("ripple_control", False) else "Aus"))
    print("3. Angle Snap: {}".format("Ein" if profile_config.get("angle_snap", False) else "Aus"))
    print("4. Debounce-Zeit: {} ms".format(profile_config.get("debounce_time", 3)))
    print("5. Zurück")
    
    perf_choice = input("\nWählen Sie eine Option (1-5): ")
    
    if perf_choice == "1":
        # Motion Sync umschalten
        enabled = not profile_config["motion_sync"]
        mouse.set_motion_sync(enabled)
    
    elif perf_choice == "2":
        # Ripple Control umschalten (nicht implementiert)
        print("Ripple Control-Einstellung ist noch nicht implementiert.")
    
    elif perf_choice == "3":
        # Angle Snap umschalten (nicht implementiert)
        print("Angle Snap-Einstellung ist noch nicht implementiert.")
    
    elif perf_choice == "4":
        # Debounce-Zeit ändern (nicht implementiert)
        print("Debounce-Zeit-Einstellung ist noch nicht implementiert.")

def handle_power_options(mouse):
    """
    Behandelt die Energiesparoptionen im interaktiven Modus
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Energiesparoptionen ---")
    active_profile = mouse.config["active_profile"]
    profile_config = mouse.config["profiles"][active_profile]
    
    print(f"Aktuelle Idle-Zeit: {profile_config['power_saving']['idle_time']} Sekunden")
    print(f"Aktueller Low-Battery-Schwellwert: {profile_config['power_saving']['low_battery_threshold']}%")
    
    idle_time = input("\nNeue Idle-Zeit in Sekunden (30-900): ")
    if not idle_time.isdigit() or not 30 <= int(idle_time) <= 900:
        print("Ungültige Eingabe. Bitte einen Wert zwischen 30 und 900 eingeben.")
        return
    
    threshold = input("Neuer Low-Battery-Schwellwert in Prozent (5-20): ")
    if not threshold.isdigit() or not 5 <= int(threshold) <= 20:
        print("Ungültige Eingabe. Bitte einen Wert zwischen 5 und 20 eingeben.")
        return
    
    mouse.set_power_saving(int(idle_time), int(threshold))

def handle_profile_saving(mouse):
    """
    Behandelt das Speichern von Einstellungen in Profilen
    
    Args:
        mouse: PulsarMouse-Objekt
    """
    print("\n--- Einstellungen in Profil speichern ---")
    profile = input("In welches Profil möchten Sie speichern? (1-4): ")
    if not profile.isdigit() or not 1 <= int(profile) <= 4:
        print("Ungültige Eingabe. Bitte eine Zahl zwischen 1 und 4 eingeben.")
        return
    
    mouse.save_to_profile(int(profile))
