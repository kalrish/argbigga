import logging

import requests
import requests.adapters
import urllib3.util.retry

import argbigga.requests.hooks

logger = logging.getLogger(
    __name__,
)


class Client(
        ):
    # FIXME: don't hardcode
    dns_address = '193.138.218.74'

    def __init__(
                self,
                requests_session=requests.Session(
                ),
            ):
        logger_basename = self.__class__.__module__ + '.' + self.__class__.__qualname__
        self.logger = logging.getLogger(
            name=logger_basename,
        )
        # requests_hooks_logger = logging.getLogger(
        #     name=logger_basename + '.requests.hooks',
        # )

        requests_session.mount(
            'https://',
            requests.adapters.HTTPAdapter(
                max_retries=urllib3.util.retry.Retry(
                    backoff_factor=0.1,
                    total=5,
                ),
            ),
        )
        # requests_session.hooks['response'].append(
        #     functools.partial(
        #         argbigga.requests.hooks.response,
        #         logger=requests_hooks_logger,
        #     ),
        # )
        self.requests_session = requests_session

    def add_wireguard_key(
                self,
                account_id,
                key,
            ):
        mullvad_api_response = self.requests_session.post(
            'https://api.mullvad.net/wg/',
            data='account=' + account_id,
            params={
                'pubkey': key,
            },
            timeout=10,
        )

        assert mullvad_api_response.ok

    def check(
                self,
            ):
        status = False

        mullvad_api_response = self.requests_session.get(
            'https://am.i.mullvad.net/json',
            timeout=10,
        )

        if mullvad_api_response.ok:
            data = mullvad_api_response.json(
            )

            mullvad_enabled = data['mullvad_exit_ip']
            if mullvad_enabled:
                self.logger.info(
                    'connected to Mullvad VPN over %s',
                    data['mullvad_server_type'],
                )
                self.logger.debug(
                    'Mullvad exit IP address: %s',
                    data['ip'],
                )
                self.logger.debug(
                    'leaving Mullvad VPN at server %s',
                    data['mullvad_exit_ip_hostname'],
                )
            else:
                self.logger.info(
                    'Mullvad VPN is disabled',
                )

            return (
                mullvad_enabled,
                data,
            )
        else:
            raise RuntimeError(
                'cannot query Mullvad API (am.i.mullvad.net)',
            )

    def get_dns_address(
                self,
            ):
        return Client.dns_address

    def list_wireguard_servers(
                self,
            ):
        servers = [
        ]

        mullvad_api_response = self.requests_session.get(
            'https://api.mullvad.net/public/relays/wireguard/v1/',
            timeout=10,
        )

        assert mullvad_api_response.ok

        data = mullvad_api_response.json(
        )

        for country in data['countries']:
            country_code = country['code']
            country_name = country['name']

            for city in country['cities']:
                city_code = city['code']
                city_name = city['name']

                relays = city['relays']
                for relay in relays:
                    relay['country_code'] = country_code
                    relay['country_name'] = country_name
                    relay['city_code'] = city_code
                    relay['city_name'] = city_name

                servers.extend(
                    relays,
                )

        return servers

    def log_in(
                self,
                account_id,
            ):
        mullvad_api_response = self.requests_session.get(
            f'https://api.mullvad.net/www/accounts/{account_id}/',
            timeout=10,
        )

        if mullvad_api_response.ok:
            data = mullvad_api_response.json(
            )

            return AuthenticatedClient(
                account=data['account'],
                requests_session=self.requests_session,
                token=data['auth_token'],
            )


class AuthenticatedClient(
        ):
    def __init__(
                self,
                account,
                token,
                requests_session,
            ):
        self.logger = logging.getLogger(
            name=self.__class__.__module__ + '.' + self.__class__.__qualname__,
        )
        self.account = account
        self.headers = {
            'Authorization': f'Token {token}',
        }
        self.requests_session = requests_session

    def delete_wireguard_key(
                self,
                key,
            ):
        mullvad_api_response = self.requests_session.post(
            'https://api.mullvad.net/www/wg-pubkeys/revoke/',
            headers=self.headers,
            params={
                'pubkey': key,
            },
            timeout=10,
        )

        assert mullvad_api_response.ok

    def enable_port(
                self,
                country,
                city,
                key,
            ):
        mullvad_api_response = self.requests_session.post(
            'https://api.mullvad.net/www/ports/add/',
            headers=self.headers,
            json={
                'city_code': f'{country}-{city}',
                'pubkey': key,
            },
            timeout=10,
        )

        assert mullvad_api_response.ok

    def list_wireguard_keys(
                self,
            ):
        mullvad_api_response = self.requests_session.get(
            'https://api.mullvad.net/www/me/',
            headers=self.headers,
            timeout=10,
        )

        assert mullvad_api_response.ok
