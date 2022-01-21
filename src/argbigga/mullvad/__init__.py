import logging

import requests
import requests.adapters
import urllib3.util.retry

logger = logging.getLogger(
    __name__,
)
requests_session = requests.Session(
)

requests_session.mount(
    'https://',
    requests.adapters.HTTPAdapter(
        max_retries=urllib3.util.retry.Retry(
            backoff_factor=0.1,
            total=5,
        ),
    ),
)


def check(
            connection_type = None,
            exit_server = None,
        ):
    status = False

    response = requests_session.get(
        'https://am.i.mullvad.net/json',
        timeout=10,
    )

    if response.ok:
        data = response.json(
        )

        mullvad_enabled = data['mullvad_exit_ip']
        if mullvad_enabled:
            logger.info(
                'Mullvad VPN is enabled',
            )
            logger.info(
                'exit IP address: %s',
                data['ip'],
            )

            conditions = [
            ]

            if connection_type:
                mullvad_connection_type = data['mullvad_server_type']
                conditions.add(
                    mullvad_connection_type == connection_type,
                )

            if exit_server:
                mullvad_exit_server = data['mullvad_exit_ip_hostname']
                conditions.add(
                    mullvad_exit_server == exit_server,
                )

            all_conditions_met = all(
                conditions,
            )
            if all_conditions_met:
                status = True
        else:
            logger.info(
                'Mullvad VPN is disabled',
            )
    else:
        logger.error(
            'cannot query Mullvad API (am.i.mullvad.net)',
        )

    return status
