import argparse
import logging
import sys

import argbigga.mullvad.wireguard
import argbigga.wireguard

aliases = [
]
description = 'Generate a configuration file suitable for `wg(8) setconf`.'
epilog = 'Without --save, configuration is output to stdout.'
help = 'generate a WireGuard configuration file for a Mullvad connection configuration'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argument_parser.add_argument(
        '--in',
        dest='mullvad_entry_server',
        help='enter Mullvad VPN at a specific server',
        metavar='HOSTNAME',
        required=True,
    )

    argument_parser.add_argument(
        '--out',
        dest='mullvad_exit_server',
        help='exit Mullvad VPN at a specific server',
        metavar='HOSTNAME',
    )

    argument_parser.add_argument(
        '--protocol',
        choices=[
            'IPv4',
            'IPv6',
        ],
        default='IPv4',
        dest='protocol',
        help='IP protocol to use to connect to the Mullvad entry server',
    )

    argument_parser.add_argument(
        '--save',
        dest='output_path',
        help='path to a file to write',
        metavar='PATH',
    )


def run(
            arguments,
        ):
    mullvad_servers = argbigga.mullvad.wireguard.get_servers(
    )

    mullvad_entry_server_parameters = mullvad_servers[arguments.mullvad_entry_server]

    if arguments.mullvad_exit_server:
        # multihopping
        mullvad_exit_server_parameters = mullvad_servers[arguments.mullvad_exit_server]
        wireguard_peer_endpoint_port = mullvad_exit_server_parameters['multihop_port']
    else:
        mullvad_exit_server_parameters = mullvad_entry_server_parameters
        wireguard_peer_endpoint_port = 51820

    wireguard_peer_key = mullvad_exit_server_parameters['public_key']

    if arguments.protocol == 'IPv4':
        wireguard_peer_endpoint_address = mullvad_entry_server_parameters['ipv4_addr_in']
    elif arguments.protocol == 'IPv6':
        wireguard_peer_endpoint_address = '[' + mullvad_entry_server_parameters['ipv6_addr_in'] + ']'

    if arguments.output_path:
        file = open(
            arguments.output_path,
            'w',
        )
    else:
        file = sys.stdout

    argbigga.wireguard.serialize_configuration(
        file=file,
        peer_endpoint_host=wireguard_peer_endpoint_address,
        peer_endpoint_port=wireguard_peer_endpoint_port,
        peer_key=wireguard_peer_key,
    )

    if arguments.output_path:
        file.close(
        )
        logger.info(
            'configuration saved to %s',
            arguments.output_path,
        )
