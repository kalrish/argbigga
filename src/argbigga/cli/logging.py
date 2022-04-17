import functools
import logging
import logging.handlers
import sys

# FIXME: do not hardcode these
default_log_levels = {
    logging.CRITICAL,
    logging.DEBUG,
    logging.ERROR,
    logging.INFO,
    logging.WARNING,
}
destinations = {
}
interim_handler = logging.handlers.MemoryHandler(
    capacity=sys.maxsize, # logging.CRITICAL
    flushLevel=sys.maxsize,
    flushOnClose=True,
    target=None,
)
iso_8601_datetime_format='%Y-%m-%dT%H:%M:%S'
logger = logging.getLogger(
    name=__name__,
)


def calculate_length_of_longest_log_level_name(
        ):
    defined_log_levels = list_defined_log_levels(
    )
    defined_log_level_names = defined_log_levels.values(
    )
    longest_log_level_name = max(
        defined_log_level_names,
        key=len,
    )
    length_of_longest_log_level_name = len(
        longest_log_level_name,
    )
    return length_of_longest_log_level_name


def enable_debugging(
        ):
    enable_http_debugging(
    )


def enable_http_debugging(
        ):
    import http.client
    http.client.HTTPConnection.debuglevel = sys.maxsize
    http.client.print = functools.partial(
        print_to_logger,
        level=logging.DEBUG,
        logger=logging.getLogger(
            name='http.client',
        ),
    )


def filter_log_record_by_level(
            record,
            level,
        ):
    let_record_through = record.levelno >= level
    return let_record_through


def finalize(
        ):
    logging.shutdown(
    )


def get_default_destination(
        ):
    # FIXME: when running as a systemd service, set 'journald' if python-systemd is available, otherwise 'syslog'
    default_destination = 'stderr'
    return default_destination


def initialize(
            destination,
            mode,
        ):
    root_logger = logging.getLogger(
        name=None,
    )

    mode_parameters = modes[mode]

    final_handler = set_up_destination_handler(
        destination=destination,
    )

    log_level = mode_parameters['level']
    root_logger.setLevel(
        level=log_level,
    )
    final_handler.setLevel(
        level=log_level,
    )
    final_handler.addFilter(
        filter=functools.partial(
            filter_log_record_by_level,
            level=log_level,
        ),
    )

    formatter = logging.Formatter(
        datefmt=iso_8601_datetime_format,
        fmt=destinations[destination]['format'][mode],
        style='%',
        validate=True, # added in Python 3.8
    )
    final_handler.setFormatter(
        formatter,
    )

    interim_handler.setTarget(
        target=final_handler,
    )
    interim_handler.close(
    )

    root_logger.removeHandler(
        interim_handler,
    )
    root_logger.addHandler(
        final_handler,
    )

    mode_parameters['post'](
    )


def list_defined_log_levels(
        ):
    '''placeholder for an eventual logging.listLogLevels()'''
    defined_log_levels = {
        log_level: logging.getLevelName(
            level=log_level,
        )
        for log_level in default_log_levels
    }
    return defined_log_levels


def lowercase_default_log_level_names(
        ):
    for log_level in default_log_levels:
        default_log_level_name = logging.getLevelName(
            level=log_level,
        )
        lowercased_log_level_name = default_log_level_name.lower(
        )
        logging.addLevelName(
            level=log_level,
            levelName=lowercased_log_level_name,
        )


def prepare(
        ):
    length_of_longest_log_level_name = calculate_length_of_longest_log_level_name(
    )

    destinations['stderr'] = {
        'format': {
            'debugging': f'%(asctime)s.%(msecs)03d [%(levelname)-{length_of_longest_log_level_name}s] %(name)s.%(funcName)s:%(lineno)d: %(message)s',
            'default': '%(levelname)s: %(message)s',
            'verbose': '%(levelname)s: %(message)s',
        },
        'handler': {
            'class': logging.StreamHandler,
            'kwargs': {
                'stream': sys.stderr,
            },
        },
    }

    destinations['syslog'] = {
        'format': {
            'debugging': '%(name)s.%(funcName)s: %(message)s',
            'default': '%(message)s',
            'verbose': '%(message)s',
        },
        'handler': {
            'class': logging.handlers.SysLogHandler,
            'kwargs': {
            },
        },
    }

    try:
        import systemd.journal
    except ModuleNotFoundError:
        logger.debug(
            'python-systemd is not available',
        )
    else:
        logger.debug(
            'python-systemd is available',
        )
        destinations['journald'] = {
            'format': destinations['syslog']['format'],
            'handler': {
                'class': systemd.journal.JournalHandler,
                'kwargs': {
                },
            },
        }

    root_logger = logging.getLogger(
        name=None,
    )

    root_logger.setLevel(
        level=logging.DEBUG,
    )

    root_logger.addHandler(
        interim_handler,
    )


def print_to_logger(
            *args,
            level,
            logger,
        ):
    '''print() replacement that outputs to a logging.Logger'''
    logger.log(
        level=level,
        msg=' '.join(
            args,
        ),
    )


def set_up_destination_handler(
            destination,
        ):
    handler_parameters = destinations[destination]['handler']
    handler_class = handler_parameters['class']
    handler = handler_class(
        **handler_parameters['kwargs'],
    )
    return handler


modes = {
    'debugging': {
        'level': logging.DEBUG,
        'post': enable_debugging,
    },
    'default': {
        'level': logging.WARNING,
        'post': lowercase_default_log_level_names,
    },
    'verbose': {
        'level': logging.INFO,
        'post': lowercase_default_log_level_names,
    },
}
