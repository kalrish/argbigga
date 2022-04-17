import argparse
import logging
import os
import secrets
import sys

import argbigga.cli.argparse
import argbigga.mullvad
import argbigga.wireguard

description = 'Generate a configuration file suitable for wg-quick(8).'
epilog = 'Without --save, configuration is output to stdout.'
# epilog = 'Without --save, configuration is output to stdout, revealing the private WireGuard key, if it was included.'
help = 'prepare deployment of Mullvad VPN over WireGuard'
# help_formatter_class = argparse.ArgumentDefaultsHelpFormatter
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
    wireguard_group = argument_parser.add_argument_group(
        # description='Control the WireGuard connection.',
        title='WireGuard options',
    )

    wireguard_group.add_argument(
        '--protocol',
        action='store',
        choices=[
            'IPv4',
            'IPv6',
        ],
        default='IPv4',
        dest='wireguard_ip_protocol',
        help='IP protocol to use to connect to the Mullvad entry server',
    )

    # wireguard_key_group = wireguard_group.add_mutually_exclusive_group(
    #     required=False,
    # )

    # wireguard_key_group.add_argument(
    #     '--wireguard-key-from-app',
    #     action='store_true',
    #     dest='wireguard_key_from_app',
    #     help='copy the private WireGuard key used by the official Mullvad app into the generated configuration',
    # )

    # wireguard_key_group.add_argument(
    #     '--wireguard-key-from-file',
    #     action='store',
    #     dest='wireguard_key_file',
    #     help='path to a file from which to load a private WireGuard key to copy into the generated configuration',
    #     metavar='PATH',
    #     type=argparse.FileType(
    #         mode='r',
    #     ),
    # )

    mullvad_group = argument_parser.add_argument_group(
        # description='Options to control the Mullvad entry and exit servers.',
        title='Mullvad options',
    )

    # mullvad_server_locations = sorted(
    #     {
    #         item
    #         for mullvad_server in mullvad_servers
    #         for item in (
    #             mullvad_server['country_code'],
    #             mullvad_server['country_code'] + ':' + mullvad_server['city_code'],
    #         )
    #     },
    # )

    # mullvad_server_names = sorted(
    #     {
    #         mullvad_server['hostname']
    #         for mullvad_server in mullvad_servers
    #     },
    # )

    mullvad_entry_group = mullvad_group.add_mutually_exclusive_group(
        required=True,
    )

    mullvad_entry_group.add_argument(
        '--entry-locations',
        action=argbigga.cli.argparse.ListDictAction,
        dest='mullvad_entry_locations',
        help='countries and cities from which to randomly pick the Mullvad server at which to enter the VPN',
        metavar='COUNTRY[:CITY]',
        nargs='+',
    )

    mullvad_entry_group.add_argument(
        '--entry-servers',
        action='store',
        dest='mullvad_entry_servers',
        help='Mullvad servers from which to randomly pick the one at which to enter the VPN',
        metavar='HOSTNAME',
        nargs='+',
    )

    mullvad_exit_group = mullvad_group.add_mutually_exclusive_group(
        required=False,
    )

    mullvad_exit_group.add_argument(
        '--exit-locations',
        action=argbigga.cli.argparse.ListDictAction,
        dest='mullvad_exit_locations',
        help='countries and cities from which to randomly pick the Mullvad server at which to exit the VPN (multihopping)',
        metavar='COUNTRY[:CITY]',
        nargs='+',
    )

    mullvad_exit_group.add_argument(
        '--exit-servers',
        action='store',
        dest='mullvad_exit_servers',
        help='Mullvad servers from which to randomly pick the one at which to exit the VPN (multihopping)',
        metavar='HOSTNAME',
        nargs='+',
    )

#    argument_parser.add_argument(
#        '--output',
#        action='store',
#        default=sys.stdout,
#        dest='output_file',
#        help='path into which to save generated configuration',
#        metavar='PATH',
#        type=argparse.FileType(
#            mode='w',
#        ),
#    )


def filter_mullvad_servers_by_locations(
            locations,
            servers,
        ):
    selected_servers = [
    ]

    for server in servers:
        server_name = server['hostname']
        server_country_name = server['country_name']
        server_country_code = server['country_code']

        try:
            selected_cities = locations[server_country_code]
        except KeyError:
            logger.debug(
                'Mullvad server %s discarded due to its country (%s)',
                server_name,
                server_country_name,
            )
        else:
            server_city_code = server['city_code']
            server_city_name = server['city_name']

            server_selected = (
                selected_cities == True
                or
                server_city_code in selected_cities
            )
            if server_selected:
                logger.debug(
                    'Mullvad server %s selected',
                    server_name,
                )
                selected_servers.append(
                    server,
                )
            else:
                logger.debug(
                    'Mullvad server %s discarded due to its city (%s in %s)',
                    server_name,
                    server_city_name,
                    server_country_name,
                )

    logger.debug(
        'selected Mullvad servers %s',
        [
            server['hostname']
            for server in selected_servers
        ],
    )

    return selected_servers


def run(
            arguments,
        ):
    mullvad_client = argbigga.mullvad.Client(
    )

    mullvad_wireguard_servers = mullvad_client.list_wireguard_servers(
    )

    mullvad_wireguard_entry_servers = (
        filter_mullvad_servers_by_locations(
            locations=arguments.mullvad_entry_locations,
            servers=mullvad_wireguard_servers,
        )
        if arguments.mullvad_entry_locations
        else [
            mullvad_wireguard_server
            for mullvad_wireguard_server in mullvad_wireguard_servers
            if mullvad_wireguard_server['hostname'] in arguments.mullvad_entry_servers
        ]
    )

    if mullvad_wireguard_entry_servers:
        mullvad_wireguard_entry_server = secrets.choice(
            mullvad_wireguard_entry_servers,
        )
        logger.info(
            'entering Mullvad VPN through server %s',
            mullvad_wireguard_entry_server['hostname'],
        )
    else:
        logger.error(
            'no Mullvad entry servers selected',
        )
        mullvad_wireguard_entry_server = None

    multihopping = (
        arguments.mullvad_exit_locations
        or
        arguments.mullvad_exit_servers
    )

    if multihopping:
        mullvad_wireguard_exit_servers = (
            filter_mullvad_servers_by_locations(
                locations=arguments.mullvad_exit_locations,
                servers=mullvad_wireguard_servers,
            )
            if arguments.mullvad_exit_locations
            else [
                mullvad_wireguard_server
                for mullvad_wireguard_server in mullvad_wireguard_servers
                if mullvad_wireguard_server['hostname'] in arguments.mullvad_exit_servers
            ]
        )

        if mullvad_wireguard_exit_servers:
            mullvad_wireguard_exit_server = secrets.choice(
                mullvad_wireguard_exit_servers,
            )
            logger.info(
                'exiting Mullvad VPN at server %s',
                mullvad_wireguard_exit_server['hostname'],
            )
        else:
            logger.error(
                'no Mullvad exit servers selected',
            )
            mullvad_wireguard_exit_server = None
    else:
        logger.info(
            'exiting Mullvad VPN at entry server',
        )
        mullvad_wireguard_exit_server = mullvad_wireguard_entry_server

    if mullvad_wireguard_entry_server and mullvad_wireguard_exit_server:
        wg_quick_config = argbigga.wireguard.WGQuickConfig(
        )

        wg_quick_config.add_peer(
            endpoint_port=(
                mullvad_wireguard_exit_server['multihop_port']
                if multihopping
                else 51820
            ),
            endpoint_host=(
                mullvad_wireguard_entry_server['ipv4_addr_in']
                if arguments.wireguard_ip_protocol == 'IPv4'
                else '[' + mullvad_wireguard_entry_server['ipv6_addr_in'] + ']'
            ),
            public_key=mullvad_wireguard_exit_server['public_key'],
        )

        wg_quick_config.set_dns_address(
            address=mullvad_client.get_dns_address(
            ),
        )

        # if arguments.wireguard_key_file:
        #     wg_quick_config.set_private_key(
        #         private_key='lalalalalala',
        #     )

        wg_quick_config.serialize(
            file=arguments.output_file,
        )

        exit_code = os.EX_OK
    else:
        exit_code = os.EX_SOFTWARE

    return argbigga.cli.subcommands.SubcommandResult(
        code=exit_code,
    )
