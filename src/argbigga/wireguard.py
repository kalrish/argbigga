import configparser
import logging

logger = logging.getLogger(
    __name__,
)


def serialize_configuration(
            file,
            peer_endpoint_host,
            peer_endpoint_port,
            peer_key,
        ):
    peer_endpoint = f'{peer_endpoint_host}:{peer_endpoint_port}'

    configuration = configparser.ConfigParser(
    )
    configuration.optionxform = lambda x: x
    configuration['Peer'] = {
        'Endpoint': peer_endpoint,
        'PublicKey': peer_key,
    }

    configuration.write(
        file,
    )
