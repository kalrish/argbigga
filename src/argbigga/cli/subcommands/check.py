import argparse
import logging
import os

import requests

import argbigga.mullvad

aliases = [
]
description = 'Check whether Mullvad VPN is active.'
epilog = f'Returns with {os.EX_OK} (EX_OK) if Mullvad VPN is active, {os.EX_CONFIG} (EX_CONFIG) if it is not, {os.EX_UNAVAILABLE} (EX_UNAVAILABLE) if the Mullvad API cannot be reached, {os.EX_PROTOCOL} (EX_PROTOCOL) if its response cannot be understood, and {os.EX_SOFTWARE} (EX_SOFTWARE) for any other error.'
help = 'check whether Mullvad VPN is active'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argument_parser.add_argument(
        '--out',
        dest='exit_server',
        help='check that traffic leaves Mullvad at a specific server',
        metavar='HOSTNAME',
    )

    argument_parser.add_argument(
        '--type',
        choices=[
            'WireGuard',
        ],
        dest='connection_type',
        help='check that Mullvad is working over a specific protocol',
    )


def run(
            arguments,
        ):
    try:
        status = argbigga.mullvad.check(
            connection_type=arguments.connection_type,
            exit_server=arguments.exit_server,
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
