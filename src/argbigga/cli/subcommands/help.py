import argparse
import logging

aliases = [
]
description = 'Explain usage of'
epilog = 'If no subcommand is passed, explain usage of the primary command.'
help = 'explain usage of subcommands'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    argument_parser.add_argument(
        'subcommand',
        help='subcommand to get help for',
        nargs='*',
    )


def run(
            arguments,
        ):
    argument_parser = tree['parser']

    if arguments.subcommand:
        subcommands = tree
        for subcommand_item in arguments.subcommand:
            subcommands = subcommands['subcommands']
            try:
                subcommand = subcommands[subcommand_item]
            except KeyError:
                argument_parser.error(
                    message='invalid subcommand',
                )
            else:
                argument_parser = subcommand['parser']

    argument_parser.print_help(
    )
