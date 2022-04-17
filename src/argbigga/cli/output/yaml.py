import logging

import yaml

logger = logging.getLogger(
    __name__,
)


def output(
            data,
            file,
        ):
    yaml.dump(
        data,
        encoding='utf-8',
        stream=file,
    )
