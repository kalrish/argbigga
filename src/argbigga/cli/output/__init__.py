import importlib
import logging

logger = logging.getLogger(
    __name__,
)


def output(
            data,
            file,
            format,
        ):
    relative_module_path = '.' + format
    module = importlib.import_module(
        name=relative_module_path,
        package=__name__,
    )
    module.output(
        data=data,
        file=file,
    )
