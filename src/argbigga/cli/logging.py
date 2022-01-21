import logging
import sys

default_log_level_names = {
    'CRITICAL',
    'DEBUG',
    'ERROR',
    'INFO',
    'WARNING',
}
logger = logging.getLogger(
    __name__,
)


def rename_log_levels(
        ):
    for default_log_level_name in default_log_level_names:
        log_level = getattr(
            logging,
            default_log_level_name,
        )
        new_log_level_name = default_log_level_name.lower(
        )
        logging.addLevelName(
            log_level,
            new_log_level_name,
        )


def set_up(
        ):
    rename_log_levels(
    )

    root_logger = logging.getLogger(
        name=None,
    )

    for existing_handler in root_logger.handlers:
        root_logger.removeHandler(
            existing_handler,
        )

    root_logger.setLevel(
        logging.WARNING,
    )


def post(
            format,
            level,
        ):
    root_logger = logging.getLogger(
        name=None,
    )

    root_logger.setLevel(
        level=level,
    )

    handler = logging.StreamHandler(
        stream=sys.stderr,
    )

    formatter = logging.Formatter(
        datefmt=None,
        fmt=format,
        style='%',
    )

    handler.setFormatter(
        formatter,
    )

    root_logger.addHandler(
        handler,
    )
