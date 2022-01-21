import logging

import argbigga.cli.argparse
import argbigga.cli.logging

logger = logging.getLogger(
    __name__,
)


def entry_point(
        ):
    argbigga.cli.logging.set_up(
    )

    logger.debug(
        'logging setup initialized',
    )

    argument_parser = argbigga.cli.argparse.build_argument_parser(
    )

    arguments = argument_parser.parse_args(
    )

    argbigga.cli.logging.post(
        **arguments.logging_kwargs,
    )

    return_code = arguments.run(
        arguments=arguments,
    )

    return return_code
