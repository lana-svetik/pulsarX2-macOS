#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/usb/usb_protocol.py
# Implementierung des USB-Kommunikationsprotokolls für Pulsar
# Updated 2025-04-17

"""
Implementierung des USB-Kommunikationsprotokolls für Pulsar X2.
Bietet Klassen und Funktionen für die direkte Kommunikation mit dem Gerät.
"""

import time
import usb.core
import usb.util
from typing import List, Dict, Any, Optional, Tuple

from ..config.settings import (VENDOR_ID, PRODUCT_ID, MODEL_NAME, SENSOR_MODEL,
                             MAX_DPI, MAX_POLLING_RATE, DPI_RANGE, DEFAULT_DPI_STAGES,
                             POLLING_RATES, LIFT_OFF_DISTANCE, BUTTON_ACTIONS,
                             CMD_GET_INFO, CMD_GET_SETTINGS, CMD_SET_DPI, CMD_SET_POLLING,
                             CMD_SET_LIFTOFF, CMD_SET_BUTTON, CMD_SET_MOTION_SYNC,
                             CMD_SET_POWER, CMD_SAVE_PROFILE)
from ..config.profiles import load_config, save_config, print_profile_settings

class PulsarMouse:
    """
    Hauptklasse für die Kommunikation mit Pulsar über USB.
    Stellt Methoden für alle Mauseinstellungen bereit.
    """
    def __init__(self, debug_mode=False):
        """
        Initialisiert die Verbindung zur Maus
        
        Args:
            debug_mode: Wenn True, werden keine tatsächlichen USB-Befehle gesendet
        """
        self.debug_mode = debug_mode
        self.device = None
        self.ep_in = None
        self.ep_out = None
        self.config = load_config()
        
        # Verbindung zur Maus herstellen, wenn nicht im Debug-Modus
        if not debug_mode:
            try:
                self.connect()
            except Exception as e:
                print(f"Fehler beim Verbinden mit der Maus: {e}")
                print("Führen Sie das Programm im Debug-Modus aus, um ohne Maus fortzufahren.")
                print("  --debug")
    
    def connect(self) -> bool:
        """
        Verbindung zur Maus herstellen
    
        Returns:
            bool: True bei erfolgreicher Verbindung, sonst False
        """
        try:
            # Maus anhand von Vendor- und Product-ID finden
            self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        
            if self.device is None:
                print("Pulsar X2 nicht gefunden.")
                print("Stellen Sie sicher, dass die Maus angeschlossen ist.")
                return False
        
            # macOS-spezifische Prüfung für den Kernel-Treiber
            try:
                # Falls die Maus von einem Kernel-Treiber verwendet wird, diesen lösen
                if self.device.is_kernel_driver_active(0):
                    try:
                        self.device.detach_kernel_driver(0)
                        print("Kernel-Treiber getrennt")
                    except usb.core.USBError as e:
                        # Unter macOS ist dies möglicherweise gar nicht nötig
                        print(f"Hinweis: Konnte Kernel-Treiber nicht trennen: {e}")
                        # Trotzdem fortfahren, da macOS oft keinen Treiber zu trennen hat
            except (AttributeError, NotImplementedError):
                # Manche macOS-Versionen unterstützen is_kernel_driver_active nicht
                print("Hinweis: Kernel-Treiber-Status konnte nicht geprüft werden (typisch für macOS)")
        
            # Konfiguration einrichten
            try:
                self.device.set_configuration()
                print(f"Verbindung zu Pulsar {MODEL_NAME} hergestellt.")
            
                # Endpunkte für die Kommunikation finden
                self._find_endpoints()
                return True
            except usb.core.USBError as e:
                if "Entity not found" in str(e):
                    print(f"Fehler: USB-Gerät konnte nicht konfiguriert werden. Möglicherweise fehlen Berechtigungen.")
                    print("Versuchen Sie, das Programm mit 'sudo' auszuführen.")
                else:
                    print(f"Fehler bei der Konfiguration des Geräts: {e}")
                return False
            
        except Exception as e:
            print(f"Fehler beim Verbinden mit der Maus: {e}")
            return False
    
    def _find_endpoints(self):
        """Findet die IN- und OUT-Endpunkte für die Kommunikation"""
        try:
            cfg = self.device.get_active_configuration()
        
            # Manchmal braucht man auf macOS einen anderen Ansatz für die Interface-Auswahl
            try:
                intf = cfg[(0, 0)]  # Interface 0, Alternative Setting 0
            except (IndexError, KeyError, TypeError):
                # Alternatives Vorgehen, falls die obige Methode fehlschlägt
                for interface in cfg:
                    intf = interface
                    break
        
            # Endpunkt für Datenempfang (von Maus zum Computer)
            self.ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
        
            # Endpunkt für Datenübertragung (vom Computer zur Maus)
            self.ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
        
            if not self.ep_in or not self.ep_out:
                raise ValueError("Konnte Endpunkte für Datenübertragung nicht finden")
            
            print(f"Endpunkte gefunden - IN: 0x{self.ep_in.bEndpointAddress:02x}, OUT: 0x{self.ep_out.bEndpointAddress:02x}")
        
        except Exception as e:
            print(f"Fehler beim Finden der Endpunkte: {e}")
            print("Dies könnte an fehlenden Berechtigungen oder einem inkompatiblen USB-Treiber liegen.")
            raise
    
    def send_command(self, command: List[int], expect_response=True, timeout=300):
        """
        Sendet einen Befehl an die Maus und liest ggf. eine Antwort
        
        Args:
            command: Liste von Bytes, die gesendet werden sollen
            expect_response: Ob eine Antwort erwartet wird
            timeout: Timeout in Millisekunden
            
        Returns:
            Die Antwort der Maus oder None
        """
        if self.debug_mode:
            cmd_str = ' '.join([f'{b:02x}' for b in command])
            print(f"DEBUG - Befehl senden: {cmd_str}")
            # Im Debug-Modus eine Dummy-Antwort zurückgeben
            return bytearray([0] * 8) if expect_response else None
        
        if not self.device or not self.ep_out:
            print("Keine Verbindung zur Maus. Befehl kann nicht gesendet werden.")
            return None
        
        try:
            # Befehl an die Maus senden
            bytes_sent = self.device.write(self.ep_out.bEndpointAddress, command)
            cmd_str = ' '.join([f'{b:02x}' for b in command])
            print(f"Befehl gesendet ({bytes_sent} Bytes): {cmd_str}")
            
            if not expect_response:
                return None
            
            # Kurze Pause für die Verarbeitung
            time.sleep(0.05)
            
            # Antwort von der Maus lesen
            try:
                response = self.device.read(self.ep_in.bEndpointAddress, 
                                           self.ep_in.wMaxPacketSize, 
                                           timeout=timeout)
                resp_str = ' '.join([f'{b:02x}' for b in response])
                print(f"Antwort erhalten: {resp_str}")
                return response
            except usb.core.USBError as e:
                if e.errno == 110:  # Timeout
                    print("Timeout beim Empfangen einer Antwort")
                else:
                    print(f"Fehler beim Lesen der Antwort: {e}")
                return None
                
        except Exception as e:
            print(f"Fehler beim Senden des Befehls: {e}")
            return None
    
    def get_device_info(self):
        """Ruft Informationen über die Maus ab"""
        print("\nRufe Geräteinformationen ab...")
        
        if self.debug_mode:
            print(f"DEBUG - Geräteinformationen:")
            print(f"Modell: {MODEL_NAME}")
            print(f"Sensor: {SENSOR_MODEL}")
            print(f"Max DPI: {MAX_DPI}")
            print(f"Max Polling Rate: {MAX_POLLING_RATE}Hz")
            return
        
        # Befehl zum Abrufen der Geräteinformationen senden
        response = self.send_command(CMD_GET_INFO)
        
        if not response:
            print("Keine Geräteinformationen verfügbar.")
            return
        
        # Hier müsste die Antwort interpretiert werden, basierend auf dem tatsächlichen Protokoll
        # Dies ist nur ein Beispiel, wie die Interpretation aussehen könnte
        print("Geräteinformationen:")
        print(f"Firmware-Version: {response[1]}.{response[2]}")
        print(f"Hardware-Revision: {response[3]}")
        print(f"Aktives Profil: {response[4]}")
    
    def set_dpi(self, dpi: int, stage: int = None):
        """
        Setzt die DPI für eine bestimmte Stufe oder die aktuelle Stufe
        
        Args:
            dpi: DPI-Wert (50-32000 in 10er-Schritten)
            stage: DPI-Stufe (1-6), wenn None, wird die aktive Stufe verwendet
        """
        # Aktives Profil abrufen
        active_profile = self.config["active_profile"]
        profile_config = self.config["profiles"][active_profile]
        
        # Wenn keine Stufe angegeben ist, die aktive Stufe verwenden
        if stage is None:
            stage = profile_config["active_dpi_stage"]
        
        # Gültigkeit der Stufe prüfen
        if not 1 <= stage <= 6:
            print(f"Warnung: Ungültige DPI-Stufe {stage}. Verwende Stufe 1.")
            stage = 1
        
        # DPI-Wert auf gültigen Bereich beschränken und auf 10er-Schritte runden
        dpi = max(50, min(MAX_DPI, dpi))
        dpi = round(dpi / 10) * 10
        
        print(f"Setze DPI für Stufe {stage} auf {dpi}...")
        
        # Konfiguration aktualisieren
        profile_config["dpi_stages"][str(stage)] = dpi
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_DPI.copy()
        command[1] = stage
        command[2] = (dpi >> 8) & 0xFF  # High-Byte
        command[3] = dpi & 0xFF         # Low-Byte
        
        self.send_command(command, expect_response=False)
        print(f"DPI für Stufe {stage} auf {dpi} gesetzt.")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def set_polling_rate(self, rate: int):
        """
        Setzt die Polling-Rate
        
        Args:
            rate: Rate in Hz (125, 250, 500, 1000, 2000, 4000, 8000)
        """
        # Gültigkeit der Rate prüfen
        if rate not in POLLING_RATES:
            closest_rate = min(POLLING_RATES, key=lambda x: abs(x - rate))
            print(f"Warnung: Polling-Rate {rate}Hz nicht unterstützt. Verwende {closest_rate}Hz.")
            rate = closest_rate
        
        # Warnung anzeigen, wenn eine hohe Rate verwendet wird
        if rate > 1000:
            print(f"Hinweis: Polling-Raten über 1000Hz erfordern einen speziellen 8K-Dongle.")
        
        print(f"Setze Polling-Rate auf {rate}Hz...")
        
        # Aktives Profil aktualisieren
        active_profile = self.config["active_profile"]
        self.config["profiles"][active_profile]["polling_rate"] = rate
        
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
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_POLLING.copy()
        command[1] = rate_value
        
        self.send_command(command, expect_response=False)
        print(f"Polling-Rate auf {rate}Hz gesetzt.")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def set_liftoff_distance(self, distance: float):
        """
        Setzt die Lift-Off-Distanz
        
        Args:
            distance: Distanz in mm (0.7, 1.0, 2.0)
        """
        # Gültigkeit der Distanz prüfen
        if distance not in LIFT_OFF_DISTANCE:
            closest_dist = min(LIFT_OFF_DISTANCE, key=lambda x: abs(x - distance))
            print(f"Warnung: Lift-Off-Distanz {distance}mm nicht unterstützt. Verwende {closest_dist}mm.")
            distance = closest_dist
        
        print(f"Setze Lift-Off-Distanz auf {distance}mm...")
        
        # Aktives Profil aktualisieren
        active_profile = self.config["active_profile"]
        self.config["profiles"][active_profile]["liftoff_distance"] = distance
        
        # Wert für das Protokoll ermitteln
        dist_values = {0.7: 0, 1.0: 1, 2.0: 2}
        dist_value = dist_values[distance]
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_LIFTOFF.copy()
        command[1] = dist_value
        
        self.send_command(command, expect_response=False)
        print(f"Lift-Off-Distanz auf {distance}mm gesetzt.")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def set_button_mapping(self, button: int, action_name: str):
        """
        Weist einer Taste eine Aktion zu
        
        Args:
            button: Tastennummer (1-5)
            action_name: Name der Aktion (aus BUTTON_ACTIONS)
        """
        # Gültigkeit der Taste prüfen
        if not 1 <= button <= 5:
            print(f"Warnung: Ungültige Taste {button}. Gültige Werte sind 1-5.")
            return
        
        # Gültigkeit der Aktion prüfen
        if action_name not in BUTTON_ACTIONS:
            print(f"Warnung: Ungültige Aktion '{action_name}'.")
            print(f"Gültige Aktionen: {', '.join(BUTTON_ACTIONS.keys())}")
            return
        
        action_code = BUTTON_ACTIONS[action_name]
        print(f"Setze Taste {button} auf '{action_name}' (Code: 0x{action_code:02x})...")
        
        # Aktives Profil aktualisieren
        active_profile = self.config["active_profile"]
        self.config["profiles"][active_profile]["buttons"][str(button)] = {
            "action": action_name,
            "code": action_code
        }
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_BUTTON.copy()
        command[1] = button
        command[2] = action_code
        
        self.send_command(command, expect_response=False)
        print(f"Taste {button} auf '{action_name}' gesetzt.")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def set_motion_sync(self, enabled: bool):
        """
        Aktiviert oder deaktiviert Motion Sync
        
        Args:
            enabled: Ob Motion Sync aktiviert werden soll
        """
        status = "aktiviert" if enabled else "deaktiviert"
        print(f"Motion Sync wird {status}...")
        
        # Aktives Profil aktualisieren
        active_profile = self.config["active_profile"]
        self.config["profiles"][active_profile]["motion_sync"] = enabled
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_MOTION_SYNC.copy()
        command[1] = 1 if enabled else 0
        
        self.send_command(command, expect_response=False)
        print(f"Motion Sync {status}.")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def set_power_saving(self, idle_time: int, low_battery_threshold: int = None):
        """
        Setzt die Energiesparoptionen
        
        Args:
            idle_time: Zeit in Sekunden, bevor die Maus in den Ruhemodus wechselt
            low_battery_threshold: Prozentwert, ab dem der Low-Power-Modus aktiviert wird
        """
        # Gültigkeit der Zeit prüfen
        if not 30 <= idle_time <= 900:
            print(f"Warnung: Ungültige Zeit {idle_time}s. Gültiger Bereich ist 30-900s.")
            idle_time = max(30, min(900, idle_time))
        
        print(f"Setze Energiesparoptionen...")
        
        # Aktives Profil aktualisieren
        active_profile = self.config["active_profile"]
        self.config["profiles"][active_profile]["power_saving"]["idle_time"] = idle_time
        
        if low_battery_threshold is not None:
            # Gültigkeit des Schwellwerts prüfen
            if not 5 <= low_battery_threshold <= 20:
                print(f"Warnung: Ungültiger Batterieschwellwert {low_battery_threshold}%. Gültiger Bereich ist 5-20%.")
                low_battery_threshold = max(5, min(20, low_battery_threshold))
            
            self.config["profiles"][active_profile]["power_saving"]["low_battery_threshold"] = low_battery_threshold
        
        # Befehl zusammenstellen und senden
        command = CMD_SET_POWER.copy()
        command[1] = idle_time & 0xFF         # Low-Byte
        command[2] = (idle_time >> 8) & 0xFF  # High-Byte
        
        if low_battery_threshold is not None:
            command[3] = low_battery_threshold
        
        self.send_command(command, expect_response=False)
        print(f"Energiesparoptionen gesetzt: Idle-Zeit = {idle_time}s")
        
        if low_battery_threshold is not None:
            print(f"Low-Battery-Schwellwert = {low_battery_threshold}%")
        
        # Konfiguration speichern
        save_config(self.config)
    
    def save_to_profile(self, profile_num: int):
        """
        Speichert die aktuellen Einstellungen in einem Profil
        
        Args:
            profile_num: Profilnummer (1-4)
        """
        if not 1 <= profile_num <= 4:
            print(f"Warnung: Ungültige Profilnummer {profile_num}. Gültige Werte sind 1-4.")
            return
        
        print(f"Speichere Einstellungen in Profil {profile_num}...")
        
        # Befehl zusammenstellen und senden
        command = CMD_SAVE_PROFILE.copy()
        command[1] = profile_num
        
        self.send_command(command, expect_response=False)
        print(f"Einstellungen in Profil {profile_num} gespeichert.")
        
        # Aktives Profil setzen
        self.config["active_profile"] = str(profile_num)
        
        # Konfiguration speichern
        save_config(self.config)
    
    def show_current_settings(self):
        """Zeigt die aktuellen Einstellungen an"""
        print_profile_settings(self.config)
