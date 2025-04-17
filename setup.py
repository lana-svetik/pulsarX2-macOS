# setup.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 Svetlana Sibiryakova
# /setup.py
# Setup-Script für die Installation des macOS-CLI für die Pulsar X2
# Updated 2025-04-17

"""
Setup-Script für die Installation des Pulsar X2 V3 macOS Konfigurationstool.
"""

from setuptools import setup, find_packages

setup(
    name="pulsar-x2-macos",
    version="1.0.0",
    description="Pulsar X2 CLI für macOS",
    author="Svetlana Sibiryakova",
    packages=find_packages(),
    install_requires=[
        "pyusb>=1.2.1",
    ],
    entry_points={
        'console_scripts': [
            'pulsar-x2-config=src.pulsar_x2_macos:main',
            'pulsar-usb-monitor=src.usb.usb_monitor:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
)
