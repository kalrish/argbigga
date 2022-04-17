import importlib
import logging
import pkgutil

logger = logging.getLogger(
    __name__,
)


def load_submodules(
            package,
            paths,
        ):
    submodules = {
    }

    iterator = pkgutil.iter_modules(
        path=paths,
    )

    logger.debug(
        'iterating over Python modules in package `%s` under paths %s',
        package,
        paths,
    )

    for module_info in iterator:
        submodule_name = module_info.name

        logger.debug(
            'iterating over module `%s`',
            submodule_name,
        )

        submodule_path = '.' + submodule_name
        submodule = importlib.import_module(
            name=submodule_path,
            package=package,
        )

        logger.debug(
            'module `%s` imported successfully',
            submodule_name,
        )

        assert not hasattr(
            submodule,
            '_submodules',
        )

        if module_info.ispkg:
            logger.debug(
                'module `%s` is a package and contains submodules',
                submodule_name,
            )

            subsubmodules = load_submodules(
                package=submodule.__name__,
                paths=submodule.__path__,
            )
            setattr(
                submodule,
                '_submodules',
                subsubmodules,
            )

        submodules[submodule_name] = submodule

    return submodules
