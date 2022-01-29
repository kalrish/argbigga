import argparse
import logging
import os

import argbigga
import argbigga.cli.subcommands
import argbigga.cli.subcommands.help
import argbigga.modutil

logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
        ):
    default_logging_kwargs = {
        'format': '%(levelname)s: %(message)s',
        'level': logging.WARNING,
    }

    argument_parser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description='Automation tool for Mullvad VPN setups on Linux',
        epilog=f'Subcommands generally output nothing to stdout. Exit codes other than {os.EX_OK} (EX_OK) usually signal failure.',
        formatter_class=argparse.HelpFormatter,
    )

    argument_parser.add_argument(
        '--version',
        action='version',
        help='display version and exit',
        version=argbigga.version,
    )

#    configuration_group = argument_parser.add_argument_group(
#        description='foo the bar',
#        title='configuration options',
#    )
#
#    configuration_group.add_argument(
#        '--config',
#        action='store',
#        default='/etc/argbigga/config.ini',
#        dest='configuration_file',
#        help='name without the .ini extension of a configuration file in /etc/argbigga/, or path to a configuration file',
#        #metavar='NAME',
#        type=argparse.FileType(
#            mode='r',
#        ),
#    )
#
#    configuration_group.add_argument(
#        '--profile',
#        action='store',
#        dest='configuration_profile',
#        help='profile to load within configuration file',
#        metavar='NAME',
#    )

#    debugging_group = argument_parser.add_argument_group(
#        description='Control emission of informational messages.',
#        title='debugging options',
#    )

    argument_parser.add_argument(
#    debugging_group.add_argument(
        '--debug',
        action='store_const',
        const={
            'format': '%(name)s: %(levelname)s: %(message)s',
            'level': logging.DEBUG,
        },
        default=default_logging_kwargs,
        dest='logging_kwargs',
        help='output debugging logs to stderr',
    )

    argument_parser.add_argument(
#    debugging_group.add_argument(
        '--verbose',
        action='store_const',
        const={
            'format': '%(levelname)s: %(message)s',
            'level': logging.INFO,
        },
        default=default_logging_kwargs,
        dest='logging_kwargs',
        help='emit informational messages to stderr',
    )

    subcommand_modules = argbigga.modutil.load_submodules(
        package=argbigga.cli.subcommands.__name__,
        paths=argbigga.cli.subcommands.__path__,
    )

    subcommand_parsers = argument_parser.add_subparsers(
        required=True,
        title='subcommands',
    )

    subtree = load_subcommand_argument_parsers(
        argument_parser=subcommand_parsers,
        subcommand_modules=subcommand_modules,
    )
    tree = {
        'parser': argument_parser,
        'subcommands': subtree,
    }

    argbigga.cli.subcommands.help.tree = tree

    return argument_parser


def load_subcommand_argument_parsers(
            argument_parser,
            subcommand_modules,
        ):
    tree = {
    }

    iterator = subcommand_modules.items(
    )
    for subcommand_name, subcommand_module in iterator:
        subcommand_parser = argument_parser.add_parser(
            subcommand_name,
            aliases=getattr(
                subcommand_module,
                'aliases',
                [
                ],
            ),
            description=subcommand_module.description,
            epilog=subcommand_module.epilog,
            formatter_class=getattr(
                subcommand_module,
                'help_formatter_class',
                argparse.HelpFormatter,
            ),
            help=subcommand_module.help,
        )

        tree[subcommand_name] = {
            'parser': subcommand_parser,
        }

        try:
            subcommand_submodules = subcommand_module._submodules
        except AttributeError:
            subcommand_module.build_argument_parser(
                argument_parser=subcommand_parser,
            )

            subcommand_parser.set_defaults(
                run=subcommand_module.run,
            )
        else:
            # subcommand contains subcommands

            def run(
                        arguments,
                    ):
                subcommand_parser.print_help(
                )

            subcommand_parser.set_defaults(
                run=run,
            )

            subsubparsers = subcommand_parser.add_subparsers(
                required=True,
                title='subcommands',
            )

            subtree = load_subcommand_argument_parsers(
                argument_parser=subsubparsers,
                subcommand_modules=subcommand_submodules,
            )

            tree['subcommands'] = subtree

    return tree
