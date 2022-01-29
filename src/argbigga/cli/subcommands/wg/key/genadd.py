import argparse
import logging
import os
import stat
import sys

import argbigga.mullvad
import argbigga.wireguard

description = 'Generate a new WireGuard key pair and add its public counterpart to a Mullvad account, saving it somewhere for later use, with the private key never being stored or logged anywhere.'
epilog = 'Without --method, PyNaCl and cryptography are tried in that order. The "selfmade" method, which can be used in absence of either library, is used only if specified explicitly. By default, the public key is not stored anywhere. This is hardly useful and possibly problematic, because it becomes hard to identify the new key in the Mullvad account.'
help = 'generate WireGuard key pair and add public counterpart to Mullvad account'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argbigga.cli.common.add_argument(
        name='--mullvad-account',
        parser=argument_parser,
    )

    argument_parser.add_argument(
        '--method',
        action='store',
        choices=[
            'cryptography',
            'PyNaCl',
            'selfmade',
        ],
        dest='key_generation_method',
        help='restrict to specific IP protocols',
    )


def run(
            arguments,
        ):
    if arguments.method == 'cryptography':
        import cryptography.hazmat.primitives
        import cryptography.hazmat.primitives.asymmetric.x25519
    elif arguments.method == 'PyNaCl':
        import nacl.public
