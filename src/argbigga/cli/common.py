import argparse
import logging

common_arguments = {
    '--mullvad-account': {
        'action': 'store',
        'dest': 'mullvad_account_id',
        # Do NOT pass your account ID on the command-line, because command-line arguments are exposed through /proc. You can use this argument in combination with process substitution, or, better yet, a combination of --config and --profile
        'help': 'path to a file-like object (such as returned by process substitution) containing the ID of the Mullvad account on which to operate',
        'metavar': 'PATH',
        'type': argparse.FileType(
            mode='r',
        ),
    },
}

logger = logging.getLogger(
    __name__,
)


def add_argument(
            name,
            parser,
        ):
    kwargs = common_arguments[name]
    parser.add_argument(
        name,
        **kwargs,
    )
