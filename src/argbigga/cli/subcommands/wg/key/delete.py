import argparse
import logging

import argbigga.cli.argparse
import argbigga.mullvad

aliases = [
    'del',
]
description = 'Remove one or more public WireGuard keys from a Mullvad account.'
epilog = None
help = 'remove WireGuard key(s) from Mullvad account'
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
        '--all',
        action='store_true',
        dest='remove_all',
        help='remove all WireGuard keys associated with the Mullvad account',
    )

    argument_parser.add_argument(
        'keys',
        action='store',
        help='public WireGuard keys to delete',
        metavar='KEY',
        nargs='*',
    )


def run(
            arguments,
        ):
    mullvad_client = argbigga.mullvad.Client(
    )

    authenticated_mullvad_client = mullvad_client.log_in(
        account_id=arguments.mullvad_account_id,
    )

    public_keys = (
        authenticated_mullvad_client.list_wireguard_keys(
        )
        if arguments.remove_all
        else arguments.public_keys
    )

    for public_key in public_keys:
        authenticated_mullvad_client.delete_wireguard_key(
            key=public_key,
        )

    return argbigga.cli.subcommands.SubcommandResult(
        code=exit_code,
    )
