#!/usr/bin/python
"""
Invokes simutack framework
"""

# Imports
import os
import sys
import glob
import argparse
import logging
import signal
import time

if __name__ == "__main__":

    time.sleep(10)

    # Parse commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help="Display debug log messages.",
                        action="store_true")  # for logging purposes
    parser.add_argument('-i', '--ip', help="IP address of carla framework server (default='localhost').",
                        default='localhost', type=str)
    parser.add_argument('-p', '--port', help="Port of carla framework server (default=2000).",
                        default=2000, type=int)
    parser.add_argument('--carla-path', help="Path to the Carla .egg file.",
                        default="", type=str)
    args = parser.parse_args()

    # Change execution path to project root
    path = os.getcwd()
    sys.path.append(path)

    print(args)

    # Add carla egg file to system path
    try:
        if args.carla_path:
            path = args.carla_path
        else:
            path = 'CARLA_0.9.13/WindowsNoEditor/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
            sys.version_info.major,
            sys.version_info.minor,
            'win-amd64' if os.name == 'nt' else 'linux-x86_64')
        sys.path.append(glob.glob(path)[0])  # Use glob to resolve * in path
    except IndexError:
        print('Failed to import Carla module!')

    # Enable to catch low level errors and generate tracebacks
    # import faulthandler
    # faulthandler.enable()

    # Init framework
    from simutack.util.Logger import logger
    from simutack.core.Controller import Controller

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Register handler to catch ctrl+c
    def signal_handler(sig, frame):
        logger.debug("SIGINT caught")
        sys.exit(0)
        # if c:
        #     logger.info("Shutting down...")
        #     c.shut_down()
    signal.signal(signal.SIGINT, signal_handler)

    # Start framework
    logger.info(f"Booting... (args: {args.ip}, {args.port})")
    c = Controller(carla_ip=args.ip, carla_port=args.port)
    logger.info("Entering main loop...")
    #c.main_loop()
    while True:
        time.sleep(1)
    #logger.info("Shutting down...")
    #c.shut_down()
