import argparse
import logging
import os
import stat
import sys

import argbigga.cli.common
import argbigga.mullvad
import argbigga.wireguard

description = 'Prepare deployment of Mullvad VPN over WireGuard.'
#'First, generate a new WireGuard key pair. Then, add the new public key to a Mullvad account, and its private counterpart to a configuration file suitable for `wg-quick(8)`. Save  saving it somewhere for later use, with the private key never being stored or logged anywhere.'
epilog = 'Without --method, cryptography and PyNaCl are tried in that order.'
#'The "selfmade" method, which can be used in absence of either library, is used only if specified explicitly. By default, the public key is not stored anywhere. This is hardly useful and possibly problematic, because it becomes hard to identify the new key in the Mullvad account.'
help = 'prepare deployment of Mullvad VPN over WireGuard'
help_formatter_class = argparse.ArgumentDefaultsHelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    wireguard_group = argument_parser.add_argument_group(
        description='Control the WireGuard connection.',
        title='WireGuard options',
    )

    wireguard_group.add_argument(
        '--wireguard-keygen-method',
        action='store',
        choices=[
            'cryptography',
            'PyNaCl',
        ],
        dest='key_generation_method',
        help='library with which to generate the WireGuard key pair',
    )

    wireguard_group.add_argument(
        '--wireguard-protocol',
        choices=[
            'IPv4',
            'IPv6',
        ],
        default='IPv4',
        dest='protocol',
        help='IP protocol to use to connect to the Mullvad entry server',
    )

    mullvad_group = argument_parser.add_argument_group(
        description='Options to control the Mullvad entry and exit servers.',
        title='Mullvad options',
    )

    argbigga.cli.common.add_argument(
        name='--mullvad-account',
        parser=mullvad_group,
    )

    mullvad_entry_group = mullvad_group.add_mutually_exclusive_group(
        required=True,
    )

    mullvad_entry_group.add_argument(
        '--mullvad-entry-locations',
        dest='mullvad_entry_locations',
        help='countries and/or cities at which to enter the Mullvad network (if multiple are specified, one will be chosen randomly)',
        metavar='SPEC',
        nargs='+',
    )

    mullvad_entry_group.add_argument(
        '--mullvad-entry-servers',
        dest='mullvad_entry_servers',
        help='Mullvad server to connect to (if multiple are specified, one will be chosen randomly)',
        metavar='MULLVAD_HOSTNAME',
        nargs='+',
    )

    mullvad_exit_group = mullvad_group.add_mutually_exclusive_group(
        required=True,
    )

    mullvad_exit_group.add_argument(
        '--mullvad-exit-locations',
        dest='mullvad_exit_locations',
        help='countries and/or cities at which to exit the Mullvad network (if multiple are specified, one will be chosen randomly)',
        metavar='SPEC',
        nargs='+',
    )

    mullvad_exit_group.add_argument(
        '--mullvad-exit-servers',
        dest='mullvad_exit_servers',
        help='Mullvad server at which to exit the Mullvad network (if multiple are specified, one will be chosen randomly)',
        metavar='MULLVAD_HOSTNAME',
        nargs='+',
    )

    output_group = argument_parser.add_argument_group(
        description='Control the output.',
        title='output options',
    )

    output_group.add_argument(
        '--output-mode',
        default=0o077,
        dest='output_mode',
        help='chmod',
        metavar='UNIX_FILE_MODE',
    )

    output_group.add_argument(
        '--output-path',
        dest='output_path',
        help='path to a file to write',
        metavar='PATH',
    )

    output_group.add_argument(
        '--output-owner',
        dest='output_owner',
        help='chown',
        metavar='USER[:GROUP]',
    )


def run(
            arguments,
        ):
    if arguments.key_generation_method == 'cryptography':
        private_key = argbigga.wireguard.generate_private_key_with_cryptography(
        )
    elif arguments.key_generation_method == 'PyNaCl':
        private_key = argbigga.wireguard.generate_private_key_with_nacl(
        )
