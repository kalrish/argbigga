import configparser
import logging

logger = logging.getLogger(
    __name__,
)


def generate_private_key_with_cryptography(
        ):
    try:
        import cryptography.hazmat.primitives
        import cryptography.hazmat.primitives.asymmetric.x25519
    except ImportError:
        logger.debug(
            'cannot import Python module "cryptography.hazmat.primitives" or "cryptography.hazmat.primitives.asymmetric.x25519"',
        )
        logger.error(
            'Python package "cryptography" is not available',
        )
    else:
        return


def generate_private_key_with_nacl(
        ):
    try:
        import nacl.public
    except ImportError:
        logger.debug(
            'cannot import Python module "nacl.public"',
        )
        logger.error(
            'Python package "nacl" is not available',
        )
    else:
        return


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
