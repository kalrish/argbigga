import argparse
import logging
import os

import requests

import argbigga.cli.argparse
import argbigga.cli.subcommands
import argbigga.mullvad

aliases = [
]
description = 'Check whether Mullvad VPN is active.'
epilog = f'Returns with {os.EX_OK} (EX_OK) if Mullvad VPN is active, {os.EX_CONFIG} (EX_CONFIG) if it is not, {os.EX_UNAVAILABLE} (EX_UNAVAILABLE) if the Mullvad API cannot be reached, {os.EX_PROTOCOL} (EX_PROTOCOL) if its response cannot be understood (e.g. because the API has changed), and {os.EX_SOFTWARE} (EX_SOFTWARE) for any other error.'
help = 'check whether Mullvad VPN is active'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argument_parser.add_argument(
        '--type',
        choices=[
            'WireGuard',
        ],
        dest='connection_type',
        help='protocol over which traffic should reach Mullvad entry server',
        required=False,
    )

    exit_group = argument_parser.add_argument_group(
        description='Check where traffic leaves Mullvad VPN.',
        title='exit checks',
    )

    exit_group = exit_group.add_mutually_exclusive_group(
        required=False,
    )

    exit_group.add_argument(
        '--exit-servers',
        dest='exit_servers',
        help='servers at which traffic should leave Mullvad VPN',
        metavar='HOSTNAME',
        nargs='+',
    )

    exit_group.add_argument(
        '--exit-locations',
        action=argbigga.cli.argparse.ListDictAction,
        dest='exit_locations',
        help='countries and cities at which traffic should leave Mullvad VPN',
        metavar='COUNTRY[:CITY]',
        nargs='+',
    )


def run(
            arguments,
        ):
    mullvad_client = argbigga.mullvad.Client(
    )

    try:
        (
            status,
            data,
        ) = mullvad_client.check(
        )
    except KeyError:
        exit_code = os.EX_PROTOCOL
    except requests.ConnectionError:
        exit_code = os.EX_UNAVAILABLE
    except requests.Timeout:
        exit_code = os.EX_UNAVAILABLE
    except:
        exit_code = os.EX_SOFTWARE
    else:
        conditions = [
            status,
        ]

        if arguments.connection_type:
            mullvad_connection_type = data['mullvad_server_type']
            conditions.add(
                mullvad_connection_type == connection_type,
            )

        if arguments.exit_locations:
            mullvad_exit_server = data['mullvad_exit_ip_hostname']
            conditions.add(
                mullvad_exit_server in arguments.exit_locations,
            )

        if arguments.exit_servers:
            mullvad_exit_server = data['mullvad_exit_ip_hostname']
            conditions.add(
                mullvad_exit_server in arguments.exit_servers,
            )

        all_conditions_met = all(
            conditions,
        )

        exit_code = (
            os.EX_OK if all_conditions_met
            else os.EX_CONFIG
        )

    return argbigga.cli.subcommands.SubcommandResult(
        code=exit_code,
    )
