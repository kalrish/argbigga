import argparse
import logging
import os

import requests

import argbigga.mullvad

aliases = [
]
description = 'Checks whether Mullvad VPN is active over WireGuard.'
epilog = 'Any exit code other than 0 means that Mullvad VPN is not active.'
help = 'check whether Mullvad VPN is active over WireGuard'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argument_parser.add_argument(
        '--out',
        dest='mullvad_exit_server',
        help='check that traffic leaves Mullvad at a specific WireGuard server',
        metavar='HOSTNAME',
    )


def run(
            arguments,
        ):
    if arguments.mullvad_exit_server:
        mullvad_exit_server = arguments.mullvad_exit_server + '-wireguard'
    else:
        mullvad_exit_server = None

    try:
        status = argbigga.mullvad.check(
            connection_type='WireGuard',
            exit_server=mullvad_exit_server,
        )
    except KeyError:
        exit_code = os.EX_PROTOCOL
    except requests.ConnectionError:
        exit_code = os.EX_UNAVAILABLE
    except requests.Timeout:
        exit_code = os.EX_UNAVAILABLE
    except:
        exit_code = OS.EX_SOFTWARE
    else:
        if status:
            exit_code = os.EX_OK
        else:
            exit_code = os.EX_CONFIG

    return exit_code
