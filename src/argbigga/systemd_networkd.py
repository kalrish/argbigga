import configparser
import logging

logger = logging.getLogger(
    __name__,
)


class NetworkdConfig(
        ):
    def __init__(
                self,
            ):
        self.logger = logging.getLogger(
            __name__,
        )

        self.configuration = configparser.ConfigParser(
        )
        self.configuration.optionxform = lambda x: x

        self.configuration['Interface'] = {
        }

    def add_peer(
                self,
                endpoint_host,
                endpoint_port,
                public_key,
            ):
        endpoint = f'{endpoint_host}:{endpoint_port}'
        self.configuration['Peer'] = {
            'Endpoint': endpoint,
            'PublicKey': public_key,
        }

    def serialize(
                self,
                file,
            ):
        self.configuration.write(
            file,
        )

    def set_private_key(
                self,
                private_key,
            ):
        self.configuration['Interface']['PrivateKey'] = private_key
