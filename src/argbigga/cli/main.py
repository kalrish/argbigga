import logging

import argbigga.cli.argparse
import argbigga.cli.logging
import argbigga.cli.output
import argbigga.cli.subcommands

logger = logging.getLogger(
    __name__,
)


def entry_point(
        ):
    argbigga.cli.logging.prepare(
    )

    argument_parser = argbigga.cli.argparse.build_argument_parser(
    )

    arguments = argument_parser.parse_args(
    )

    argbigga.cli.logging.initialize(
        destination=arguments.logs_destination,
        mode=arguments.logging_mode,
    )

    execute_subcommand = arguments.subcommand
    subcommand_result = execute_subcommand(
        arguments=arguments,
    )

    assert isinstance(
            subcommand_result,
            argbigga.cli.subcommands.SubcommandResult,
        )

    if subcommand_result.data is not None:
        argbigga.cli.output.output(
            data=subcommand_result.data,
            file=arguments.output_file,
            format=arguments.output_format,
        )

    argbigga.cli.logging.finalize(
    )

    return subcommand_result.code
