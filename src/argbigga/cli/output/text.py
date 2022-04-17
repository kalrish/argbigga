import logging

logger = logging.getLogger(
    __name__,
)


def output(
            data,
            file,
        ):
    print(
        data,
        file=file,
    )
    # file.write(
    #     data,
    # )
    # file.write(
    #     "\n",
    # )
