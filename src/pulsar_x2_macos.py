#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/pulsar_x2_macos.py
# Setup-Script für die Installation des macOS-CLI für die Pulsar X2
# Updated 2025-04-17

"""
Hauptmodul für das macOS-CLI für die Pulsar X2.
Verarbeitet Kommandozeilenparameter und startet die entsprechenden Funktionen.
"""

import sys
import argparse
import signal
from typing import Dict, Any, Optional

from .usb.usb_protocol import PulsarMouse
from .config.settings import (DPI_RANGE, POLLING_RATES, LIFT_OFF_DISTANCE, 
                              MAX_DPI, MAX_POLLING_RATE)
from .config.profiles import load_config, save_config
from .ui.interactive import interactive_cli

def parse_arguments():
    """Kommandozeilenargumente verarbeiten"""
    parser = argparse.ArgumentParser(description='Pulsar X2 macOS-CLI')
    
    parser.add_argument('--debug', action='store_true', 
                        help='Debug-Modus (keine tatsächliche USB-Kommunikation)')
    parser.add_argument('--dpi', type=int, 
                        help=f'DPI-Wert setzen (50-{MAX_DPI})')
    parser.add_argument('--stage', type=int, default=1, 
                        help='DPI-Stufe (1-6, Standard: 1)')
    parser.add_argument('--polling', type=int, choices=POLLING_RATES, 
                        help='Polling-Rate setzen (Hz)')
    parser.add_argument('--liftoff', type=float, choices=LIFT_OFF_DISTANCE, 
                        help='Lift-Off-Distanz setzen (mm)')
    parser.add_argument('--motion-sync', type=str, choices=['on', 'off'], 
                        help='Motion Sync ein-/ausschalten')
    parser.add_argument('--idle-time', type=int, 
                        help='Idle-Zeit für Energiesparmodus setzen (30-900 Sekunden)')
    parser.add_argument('--battery-threshold', type=int, 
                        help='Low-Battery-Schwellwert setzen (5-20%)')
    parser.add_argument('--profile', type=int, choices=[1, 2, 3, 4], 
                        help='Aktives Profil setzen')
    parser.add_argument('--info', action='store_true', 
                        help='Geräteinformationen anzeigen')
    parser.add_argument('--settings', action='store_true', 
                        help='Aktuelle Einstellungen anzeigen')
    
    return parser.parse_args()

def main():
    """Hauptfunktion des Programms"""
    args = parse_arguments()
    
    try:
        # Sicherstellen, dass bei Terminierung durch Strg+C aufgeräumt wird
        def signal_handler(sig, frame):
            print("\nProgramm wird beendet...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Mausobjekt initialisieren
        mouse = PulsarMouse(debug_mode=args.debug)
        
        # Kommandozeilenargumente verarbeiten
        if args.dpi:
            mouse.set_dpi(args.dpi, args.stage)
        
        if args.polling:
            mouse.set_polling_rate(args.polling)
        
        if args.liftoff:
            mouse.set_liftoff_distance(args.liftoff)
        
        if args.motion_sync:
            mouse.set_motion_sync(args.motion_sync == 'on')
        
        if args.idle_time:
            battery_threshold = args.battery_threshold if args.battery_threshold else None
            mouse.set_power_saving(args.idle_time, battery_threshold)
        
        if args.profile:
            mouse.save_to_profile(args.profile)
        
        if args.info:
            mouse.get_device_info()
        
        if args.settings:
            mouse.show_current_settings()
        
        # Wenn keine Argumente angegeben wurden oder nur --debug, interaktiven Modus starten
        if all(arg is None or (isinstance(arg, bool) and arg is False) for arg in vars(args).values()) or (args.debug and len(sys.argv) == 2):
            interactive_cli(mouse)
            
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer beendet.")
    except Exception as e:
        print(f"Fehler: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
