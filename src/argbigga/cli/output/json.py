import json
import logging

logger = logging.getLogger(
    __name__,
)


def output(
            data,
            file,
        ):
    json.dump(
        data,
        file,
    )
