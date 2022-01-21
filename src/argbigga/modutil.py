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
    for module_info in iterator:
        submodule_name = module_info.name
        submodule_path = '.' + submodule_name
        submodule = importlib.import_module(
            name=submodule_path,
            package=package,
        )

        assert not hasattr(
            submodule,
            '_submodules',
        )

        if module_info.ispkg:
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
