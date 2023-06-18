#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import logging

# Configure logger
logger = logging.getLogger("Autopilot")    # Modul name
logger.setLevel(logging.WARNING)           # Log level
log_format = logging.Formatter(
    '%(levelname)s:%(name)s:\t%(message)s')  # Log Format
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_format)
logger.addHandler(log_handler)
logger.propagate = False
