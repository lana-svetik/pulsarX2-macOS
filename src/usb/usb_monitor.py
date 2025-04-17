#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /src/usb/usb_monitor.py
# USB-Monitor für das Reverse-Engineering der Pulsar X2
# Updated 2025-04-17
"""
USB-Monitor für das Reverse Engineering der Pulsar X2.
Überwacht die USB-Kommunikation und protokolliert Befehle und Antworten.
"""

import sys
import time
import argparse
import usb.core
import usb.util
from datetime import datetime
from typing import Optional, Tuple, List

from ..config.settings import VENDOR_ID, PRODUCT_ID, MODEL_NAME

def find_device():
    """
    Sucht nach der Pulsar X2 und gibt das Geräteobjekt zurück
    
    Returns:
        usb.core.Device: Das USB-Geräteobjekt der Maus
        
    Raises:
        SystemExit: Wenn die Maus nicht gefunden wird
    """
    device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if device is None:
        print("Fehler: Pulsar X2 nicht gefunden.")
        print("Stellen Sie sicher, dass die Maus angeschlossen ist.")
        sys.exit(1)
    return device

def setup_device(device):
    """
    Bereitet das Gerät für die Kommunikation vor
    
    Args:
        device: USB-Geräteobjekt
        
    Raises:
        SystemExit: Bei kritischen Fehlern
    """
    # Überprüfen, ob das Gerät von einem Kernel-Treiber verwendet wird
    if device.is_kernel_driver_active(0):
        try:
            device.detach_kernel_driver(0)
            print("Kernel-Treiber erfolgreich getrennt.")
        except usb.core.USBError as e:
            print(f"Warnung: Konnte Kernel-Treiber nicht trennen: {e}")
            pass
    
    # Konfiguration einrichten
    try:
        device.set_configuration()
        print("Gerät erfolgreich konfiguriert.")
    except usb.core.USBError as e:
        print(f"Fehler bei der Konfiguration des Geräts: {e}")
        sys.exit(1)

def find_endpoints(device) -> Tuple[usb.core.Endpoint, usb.core.Endpoint]:
    """
    Findet und gibt die IN- und OUT-Endpunkte zurück
    
    Args:
        device: USB-Geräteobjekt
        
    Returns:
        Tuple[usb.core.Endpoint, usb.core.Endpoint]: IN- und OUT-Endpunkte
        
    Raises:
        SystemExit: Wenn die Endpunkte nicht gefunden werden können
    """
    cfg = device.get_active_configuration()
    interface = cfg[(0,0)]
    
    ep_in = usb.util.find_descriptor(
        interface,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
    )
    
    ep_out = usb.util.find_descriptor(
        interface,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    
    if ep_in is None or ep_out is None:
        print("Fehler: Konnte die Endpunkte nicht finden.")
        sys.exit(1)
    
    print(f"IN-Endpunkt gefunden: 0x{ep_in.bEndpointAddress:02x}")
    print(f"OUT-Endpunkt gefunden: 0x{ep_out.bEndpointAddress:02x}")
    
    return ep_in, ep_out

def monitor_traffic(device, duration=60, log_file=None):
    """
    Überwacht die USB-Kommunikation für eine bestimmte Zeit
    
    Args:
        device: USB-Geräteobjekt
        duration: Überwachungsdauer in Sekunden
        log_file: Optional, Dateiname für die Protokollierung
    """
    ep_in, ep_out = find_endpoints(device)
    
    # Log-Datei öffnen, falls angegeben
    log_handle = None
    if log_file:
        try:
            log_handle = open(log_file, 'w')
            log_handle.write("Zeitstempel,Richtung,Daten\n")
            print(f"Protokollierung in '{log_file}' gestartet.")
        except IOError as e:
            print(f"Fehler beim Öffnen der Log-Datei: {e}")
            log_handle = None
    
    print(f"\nÜberwache USB-Verkehr für {duration} Sekunden...")
    print("Bewegen Sie die Maus oder verwenden Sie die Windows-Software, um Befehle zu senden.")
    print("Drücken Sie Strg+C, um die Überwachung vorzeitig zu beenden.\n")
    
    end_time = time.time() + duration
    try:
        while time.time() < end_time:
            # Versuchen, Daten vom IN-Endpunkt zu lesen (von der Maus zum Computer)
            try:
                data = device.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=100)
                if data:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    data_str = ' '.join([f'{b:02x}' for b in data])
                    print(f"[{timestamp}] IN: {data_str}")
                    
                    if log_handle:
                        log_handle.write(f"{timestamp},IN,{data_str}\n")
                        log_handle.flush()
            except usb.core.USBError as e:
                if e.errno != 110:  # Timeout-Fehler ignorieren
                    print(f"Fehler beim Lesen vom IN-Endpunkt: {e}")
            
            # Warten, um die CPU-Auslastung zu reduzieren
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\nÜberwachung durch Benutzer beendet.")
    
    finally:
        print("\nÜberwachung beendet.")
        if log_handle:
            log_handle.close()
            print(f"Protokoll gespeichert in '{log_file}'.")

def send_command(device, command: List[int], description=None):
    """
    Sendet einen Befehl an die Maus und liest die Antwort
    
    Args:
        device: USB-Geräteobjekt
        command: Liste von Bytes, die gesendet werden sollen
        description: Optional, Beschreibung des Befehls für die Ausgabe
        
    Returns:
        bytearray: Die Antwort der Maus oder None bei Fehler
    """
    ep_in, ep_out = find_endpoints(device)
    
    if description:
        print(f"\nSende Befehl: {description}")
    
    cmd_str = ' '.join([f'{b:02x}' for b in command])
    print(f"OUT: {cmd_str}")
    
    try:
        bytes_sent = device.write(ep_out.bEndpointAddress, command)
        print(f"Bytes gesendet: {bytes_sent}")
        
        # Versuchen, eine Antwort zu lesen
        try:
            time.sleep(0.1)  # Kurze Pause für die Verarbeitung
            response = device.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=300)
            
            resp_str = ' '.join([f'{b:02x}' for b in response])
            print(f"IN: {resp_str}")
            return response
        except usb.core.USBError as e:
            if e.errno == 110:  # Timeout
                print("Keine Antwort erhalten (Timeout).")
            else:
                print(f"Fehler beim Lesen der Antwort: {e}")
            return None
    
    except usb.core.USBError as e:
        print(f"Fehler beim Senden des Befehls: {e}")
        return None

def analyze_log(log_file: str):
    """
    Analysiert eine Protokolldatei und versucht, Muster zu erkennen
    
    Args:
        log_file: Pfad zur Protokolldatei
    """
    print(f"Analysiere Protokolldatei: {log_file}")
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        if len(lines) <= 1:
            print("Protokolldatei ist leer oder enthält nur die Kopfzeile.")
            return
            
        # Kopfzeile überspringen
        data_lines = lines[1:]
        in_packets = []
        out_packets = []
        
        for line in data_lines:
            parts = line.strip().split(',')
            if len(parts) < 3:
                continue
                
            timestamp, direction, data_str = parts
            data = [int(b, 16) for b in data_str.split()]
            
            if direction == "IN":
                in_packets.append((timestamp, data))
            elif direction == "OUT":
                out_packets.append((timestamp, data))
        
        print(f"Insgesamt {len(in_packets)} IN-Pakete und {len(out_packets)} OUT-Pakete gefunden.")
        
        # Häufig vorkommende Befehlsmuster identifizieren
        if out_packets:
            print("\nHäufig vorkommende Befehlsmuster:")
            
            # Pakete nach dem ersten Byte gruppieren (Befehlstyp)
            command_groups = {}
            for timestamp, data in out_packets:
                if not data:
                    continue
                    
                cmd_type = data[0]
                if cmd_type not in command_groups:
                    command_groups[cmd_type] = []
                    
                command_groups[cmd_type].append(data)
            
            # Häufigste Befehle ausgeben
            for cmd_type, commands in sorted(command_groups.items()):
                print(f"\nBefehlstyp 0x{cmd_type:02x} ({len(commands)} Vorkommen):")
                
                # Beispiele anzeigen
                for i, cmd in enumerate(commands[:3]):
                    cmd_str = ' '.join([f'{b:02x}' for b in cmd])
                    print(f"  Beispiel {i+1}: {cmd_str}")
                
                # Variationen in den Parametern identifizieren
                if len(commands) > 1 and len(commands[0]) > 1:
                    variations = []
                    for byte_pos in range(1, len(commands[0])):
                        values = set(cmd[byte_pos] for cmd in commands if len(cmd) > byte_pos)
                        if len(values) > 1:
                            variations.append((byte_pos, values))
                    
                    if variations:
                        print("  Parameteränderungen:")
                        for byte_pos, values in variations:
                            val_str = ', '.join([f'0x{v:02x}' for v in sorted(values)])
                            print(f"    Byte {byte_pos}: {val_str}")
        
        # Korrelationen zwischen Befehlen und Antworten
        if out_packets and in_packets:
            print("\nKorrelation zwischen Befehlen und Antworten:")
            
            # Einfache zeitbasierte Korrelation
            max_time_diff = 0.5  # 500ms
            correlated_pairs = []
            
            for out_ts, out_data in out_packets:
                out_time = datetime.strptime(out_ts, '%Y-%m-%d %H:%M:%S.%f')
                
                # Nächste Antwort nach diesem Befehl finden
                for in_ts, in_data in in_packets:
                    in_time = datetime.strptime(in_ts, '%Y-%m-%d %H:%M:%S.%f')
                    time_diff = (in_time - out_time).total_seconds()
                    
                    if 0 < time_diff < max_time_diff:
                        correlated_pairs.append((out_data, in_data, time_diff))
                        break
            
            # Beispiele für korrelierte Paare anzeigen
            for i, (out_data, in_data, time_diff) in enumerate(correlated_pairs[:5]):
                if i >= 5:  # Maximal 5 Beispiele
                    break
                    
                out_str = ' '.join([f'{b:02x}' for b in out_data])
                in_str = ' '.join([f'{b:02x}' for b in in_data])
                print(f"\nPaar {i+1} (Zeitdifferenz: {time_diff*1000:.1f}ms):")
                print(f"  Befehl:  {out_str}")
                print(f"  Antwort: {in_str}")
            
            if len(correlated_pairs) > 5:
                print(f"\n... und {len(correlated_pairs) - 5} weitere Paare.")
        
        print("\nProtokollanalyse abgeschlossen.")
        
    except Exception as e:
        print(f"Fehler bei der Analyse der Protokolldatei: {e}")

def main():
    """Hauptfunktion des USB-Monitors"""
    parser = argparse.ArgumentParser(description='Pulsar X2 USB-Monitor für macOS')
    
    parser.add_argument('--monitor', '-m', action='store_true', help='USB-Verkehr überwachen')
    parser.add_argument('--duration', '-d', type=int, default=60, help='Überwachungsdauer in Sekunden (Standard: 60)')
    parser.add_argument('--log', '-l', type=str, help='Dateiname für die Protokollierung')
    parser.add_argument('--command', '-c', type=str, help='Befehl an die Maus senden (Hex-Bytes, durch Leerzeichen getrennt)')
    parser.add_argument('--description', type=str, help='Beschreibung des Befehls')
    parser.add_argument('--analyze', '-a', type=str, help='Protokolldatei analysieren')
    
    args = parser.parse_args()
    
    try:
        if args.analyze:
            analyze_log(args.analyze)
            return
            
        # Gerät suchen und vorbereiten
        device = find_device()
        setup_device(device)
        
        if args.command:
            # Befehl senden
            try:
                cmd_bytes = [int(b, 16) for b in args.command.split()]
                send_command(device, cmd_bytes, args.description)
            except ValueError:
                print("Fehler: Ungültiges Befehlsformat. Verwenden Sie Hex-Bytes, getrennt durch Leerzeichen.")
                print("Beispiel: --command '05 01 01 06 40 00 00 00'")
                sys.exit(1)
        
        elif args.monitor or not (args.command or args.analyze):
            # USB-Verkehr überwachen (Standard, wenn kein anderer Befehl angegeben wurde)
            monitor_traffic(device, args.duration, args.log)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer beendet.")
    
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
