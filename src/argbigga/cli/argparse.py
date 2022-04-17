import argparse
import logging
import os
import sys

import argbigga
import argbigga.cli.subcommands
import argbigga.cli.subcommands.help
import argbigga.modules

logger = logging.getLogger(
    __name__,
)


class FileLoadType(
            argparse.FileType,
        ):
    def __init__(
                self,
            ):
        self.parent = super(
        )
        self.parent.__init__(
            mode='r',
        )

    def __call__(
                self,
                string,
            ):
        file = self.parent.__call__(
            string,
        )
        content = file.read(
        )
        account_number = content.rstrip(
            "\n",
        )
        return account_number


# {
#    'foo': [
#        'a',
#        'b',
#    ],
#    'bar': True,
# }
class ListDictAction(
            argparse.Action,
        ):
    def __init__(
                self,
                option_strings,
                dest,
                nargs,
                **kwargs,
            ):
        super(
        ).__init__(
            option_strings,
            dest,
            nargs,
            default={
            },
            type=colon_separated_key_value_pair,
            **kwargs,
        )

    def __call__(
                self,
                parser,
                namespace,
                values,
                option_string,
            ):
        dictionary = getattr(
            namespace,
            self.dest,
        )

        for value in values:
            key = value[0]

            try:
                new_value = value[1]
            except IndexError:
                logger.debug(
                    "key '%s': all enabled",
                    key,
                )
                dictionary[key] = True
            else:
                logger.debug(
                    "key '%s': new value: '%s'",
                    key,
                    new_value,
                )
                try:
                    existing_values = dictionary[key]
                except KeyError:
                    dictionary[key] = [
                        new_value,
                    ]
                else:
                    existing_values.append(
                        new_value,
                    )

        setattr(
            namespace,
            self.dest,
            dictionary,
        )


def build_argument_parser(
        ):
    argument_parser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description='Automation tool for Mullvad VPN setups on Linux',
        # epilog=f'Subcommands generally output nothing to stdout. Exit codes other than {os.EX_OK} (EX_OK) usually signal failure.',
        epilog=f'Exit codes other than {os.EX_OK} (EX_OK) usually signal failure.',
        formatter_class=argparse.HelpFormatter,
    )

    argument_parser.add_argument(
        '--version',
        action='version',
        help='display version and exit',
        version=argbigga.version,
    )

    logging_group = argument_parser.add_argument_group(
        title='logging options',
    )

    logging_group.add_argument(
        '--debug',
        action='store_const',
        const='debugging',
        dest='logging_mode',
        help='explain execution in detail',
    )

    logging_group.add_argument(
        '--logs-destination',
        action='store',
        choices=argbigga.cli.logging.destinations.keys(
        ),
        default=argbigga.cli.logging.get_default_destination(
        ),
        dest='logs_destination',
        help='system into which to output logs',
    )

    logging_group.add_argument(
        '--verbose',
        action='store_const',
        const='verbose',
        dest='logging_mode',
        help='emit informational messages',
    )

    argument_parser.set_defaults(
        logging_mode='default',
    )

    subcommand_modules = argbigga.modules.load_submodules(
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


def colon_separated_key_value_pair(
            argument,
        ):
    items = argument.split(
        sep=':',
    )
    amount_of_items = len(
        items,
    )
    if amount_of_items == 1:
        return items
    if amount_of_items == 2:
        if not items[1]:
            del items[1]
        return items
    else:
        raise argparse.ArgumentTypeError(
            f'argument "{argument}" contains multiple colons (:)',
        )


def load_subcommand_argument_parsers(
            argument_parser,
            subcommand_modules,
        ):
    tree = {
    }

    iterator = subcommand_modules.items(
    )
    for subcommand_name, subcommand_module in iterator:
        logger.debug(
            'loading subcommand `%s`',
            subcommand_name,
        )

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
            parents=getattr(
                subcommand_module,
                'parents',
                [
                ],
            ),
        )

        tree[subcommand_name] = {
            'parser': subcommand_parser,
        }

        try:
            subcommand_submodules = subcommand_module._submodules
        except AttributeError:
            logger.debug(
                'subcommand `%s` does not contain any subcommands',
                subcommand_name,
            )

            try:
                build_subcommand_argument_parser = subcommand_module.build_argument_parser
            except AttributeError:
                pass
            else:
                build_subcommand_argument_parser(
                    argument_parser=subcommand_parser,
                )

            subcommand_parser.set_defaults(
                subcommand=subcommand_module.run,
            )
        else:
            logger.debug(
                'subcommand `%s` contains subcommands',
                subcommand_name,
            )

            def run(
                        arguments,
                    ):
                subcommand_parser.print_help(
                )

            subcommand_parser.set_defaults(
                subcommand=run,
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


data_output = argparse.ArgumentParser(
    add_help=False,
)

data_output_group = data_output.add_argument_group(
    title='output options',
)

data_output_group.add_argument(
    '--output-format',
    action='store',
    choices=[
        'json',
        'text',
        'yaml',
    ],
    default='json',
    dest='output_format',
    help='format in which to output data',
)

data_output_group.add_argument(
    '--output-to',
    action='store',
    default=sys.stdout,
    # default='-',
    dest='output_file',
    help='path on which to save data',
    metavar='PATH',
    type=argparse.FileType(
        mode='w',
    ),
)


mullvad_account = argparse.ArgumentParser(
    add_help=False,
)

mullvad_account_group = mullvad_account.add_argument_group(
    title='Mullvad account number',
)

mullvad_account_group = mullvad_account_group.add_mutually_exclusive_group(
    required=True,
)

# Passing Mullvad account numbers as command-line arguments would not be secure,
# because command-line arguments are exposed through /proc.
# Loading them from files is more secure,
# and still flexible thanks to shell process substitution.
mullvad_account_group.add_argument(
    '--mullvad-account-number-from-file',
    action='store',
    dest='mullvad_account_id',
    help='path to a file from which to load the Mullvad account number',
    # help='path to a file-like object (such as returned by process substitution) containing the number of the Mullvad account on which to operate',
    metavar='PATH',
    type=FileLoadType(
    ),
)

mullvad_account_group.add_argument(
    '--mullvad-account-number-from-app',
    action='store_true',
    dest='mullvad_account_id',
    help='load Mullvad account number from /etc/mullvad-vpn/settings.json',
)
