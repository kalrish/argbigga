import logging

import argbigga.mullvad

logger = logging.getLogger(
    __name__,
)


def add_key(
            account,
            key,
        ):
    response = argbigga.mullvad.requests_session.post(
        'https://api.mullvad.net/wg/',
        data='account=' + account,
        params={
            'pubkey': key,
        },
        timeout=10,
    )


def get_servers(
        ):
    servers = {
    }

    response = argbigga.mullvad.requests_session.get(
        'https://api.mullvad.net/public/relays/wireguard/v1/',
        timeout=10,
    )

    if response.ok:
        data = response.json(
        )

        countries = data['countries']
        for country in countries:
            cities = country['cities']
            for city in cities:
                relays = city['relays']
                for relay in relays:
                    full_server_name = relay['hostname']
                    server_name = full_server_name[:-10]
                    servers[server_name] = relay

    return servers
