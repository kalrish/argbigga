import logging

logger = logging.getLogger(
    __name__,
)


def request(
            request,
            logger,
            *args,
            **kwargs,
        ):

    iterator = request.headers.items(
    )
    for header, value in iterator:
        logger.debug(
            'header: %s: %s',
            header,
            value,
        )

    if request.encoding:
        logger.debug(
            'body (%s): %s',
            request.encoding,
            request.text,
        )


def response(
            response,
            logger,
            *args,
            **kwargs,
        ):
    logger.debug(
        'status: %i (%s)',
        response.status_code,
        response.reason,
    )

    iterator = response.headers.items(
    )
    for header, value in iterator:
        logger.debug(
            'header: %s: %s',
            header,
            value,
        )

    if response.encoding:
        logger.debug(
            'body (%s): %s',
            response.encoding,
            response.text,
        )
