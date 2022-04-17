import argparse
import logging

import argbigga.cli.argparse
import argbigga.mullvad

description = 'Add a public WireGuard key to a Mullvad account and print the associated WireGuard address range(s).'
epilog = 'The returned address range(s) are associated to the Mullvad account and must be kept private.'
help = 'add WireGuard key to Mullvad account'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)
parents = [
    argbigga.cli.argparse.mullvad_account,
]


def build_argument_parser(
            argument_parser,
        ):
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

    return argbigga.cli.subcommands.SubcommandResult(
        code=exit_code,
        data=addresses,
    )
