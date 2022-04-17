import argparse
import logging
import os

import argbigga.cli.argparse
import argbigga.mullvad

description = 'List public WireGuard keys associated with a Mullvad account.'
epilog = None
help = 'list WireGuard keys linked to Mullvad account'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)
parents = [
    argbigga.cli.argparse.mullvad_account,
]


def run(
            arguments,
        ):
    mullvad_client = argbigga.mullvad.Client(
    )

    authenticated_mullvad_client = mullvad_client.log_in(
        account_id=arguments.mullvad_account_id,
    )

    keys = [
        peer['key']['public']
        for peer in authenticated_mullvad_client.account['wg_peers']
    ]

    return argbigga.cli.subcommands.SubcommandResult(
        data=keys,
    )
