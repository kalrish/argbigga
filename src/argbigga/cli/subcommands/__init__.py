import logging
import os

logger = logging.getLogger(
    __name__,
)


class SubcommandResult(
        ):
    def __init__(
                self,
                code=os.EX_OK,
                data=None,
            ):
        self.code = code
        self.data = data
