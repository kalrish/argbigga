import argparse
import logging
import os
import stat
import sys

import argbigga.cli.common
import argbigga.mullvad
import argbigga.wireguard

description = 'Add a public WireGuard key to a Mullvad account and return the associated WireGuard address range(s).'
epilog = 'The returned address range(s) are associated to the Mullvad account and must be kept private.'
help = 'add public WireGuard key to Mullvad account'
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
        'public_key',
        action='store',
        help='public WireGuard keys to add, in Base64',
        metavar='KEY',
    )


def run(
            arguments,
        ):
    logger.debug(
        'public key: %s',
        arguments.public_key,
    )
