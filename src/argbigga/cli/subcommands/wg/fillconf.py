import argparse
import logging
import os
import stat
import sys

import argbigga.mullvad
import argbigga.wireguard

aliases = [
]
description = 'Generate configuration files suitable for `wg(8) setconf` for combinations of Mullvad entry and exit servers and IP protocols.'
epilog = 'If executed frequently with different parameters but the same output directory, consider --empty to clean up configuration files generated in previous runs. COUNTRY may be a country\'s name (e.g. "Australia") or code (e.g. `au`). Likewise, CITY may be a city\'s name (e.g. "Melbourne") or code (e.g. `mel`). When specifying HOSTNAME, omit the `-wireguard` suffix, because it is implied.'
#epilog = 'By default, configuration files are generated for every possible combination. This results in a huge number of files, a high storage consumption and a long execution time. The selection can and probably should be restricted.'
help = 'generate WireGuard configuration files for multiple Mullvad connection configurations'
help_formatter_class = argparse.HelpFormatter
logger = logging.getLogger(
    __name__,
)


def build_argument_parser(
            argument_parser,
        ):
#    mullvad_server_names = list(
#        mullvad_servers.keys(
#        ),
#    )

    argument_parser.add_argument(
        '--empty',
        action=argparse.BooleanOptionalAction,
        default=False,
        dest='empty_directory',
        help='whether to empty output directory if it already exists',
    )

    argument_parser.add_argument(
        '--in-cities',
        action='store',
        dest='entry_cities',
        help='restrict entry servers to specific cities',
        metavar='CITY',
        nargs='+',
    )

    argument_parser.add_argument(
        '--in-countries',
        action='store',
        dest='entry_countries',
        help='restrict entry servers to specific countries',
        metavar='COUNTRY',
        nargs='+',
    )

    argument_parser.add_argument(
        '--in-servers',
        action='store',
#        default=mullvad_server_names,
        dest='entry_servers',
        help='restrict to specific entry servers',
        metavar='HOSTNAME',
        nargs='+',
    )

    argument_parser.add_argument(
        '--multihopping',
        action=argparse.BooleanOptionalAction,
        default=False,
        dest='multihopping',
        help='whether to generate multihopping configurations (implicitly enabled when any of the --out-* options is specified)',
    )

    argument_parser.add_argument(
        '--out-cities',
        action='store',
        dest='exit_cities',
        help='restrict exit servers to specific cities',
        metavar='CITY',
        nargs='+',
    )

    argument_parser.add_argument(
        '--out-countries',
        action='store',
        dest='exit_countries',
        help='restrict exit servers to specific countries',
        metavar='COUNTRY',
        nargs='+',
    )

    argument_parser.add_argument(
        '--out-servers',
        action='store',
#        default=mullvad_server_names,
        dest='exit_servers',
        help='restrict to specific exit servers',
        metavar='HOSTNAME',
        nargs='+',
    )

    argument_parser.add_argument(
        '--prefix',
        action='store',
        default='mullvad-',
        dest='filename_prefix',
        help='prefix for generated files',
    )

    argument_parser.add_argument(
        '--protocols',
        action='store',
        choices=[
            'IPv4',
            'IPv6',
        ],
        default=[
            'IPv4',
            'IPv6',
        ],
        dest='protocols',
        help='restrict to specific IP protocols',
        nargs='+',
    )

    argument_parser.add_argument(
        '--save',
        dest='directory',
        help='directory in which to save generated configuration files',
        metavar='PATH',
        required=True,
    )


def run(
            arguments,
        ):
    os_open_supports_dir_fd = os.open in os.supports_dir_fd
    if os_open_supports_dir_fd:
        try:
            os.mkdir(
                path=arguments.directory,
            )
        except FileExistsError:
            logger.debug(
                'directory %s already exists',
                arguments.directory,
            )

            if arguments.empty_directory:
                iterator = os.fwalk(
                    top=arguments.directory,
                    topdown=False,
                )
                for root_dir, directories, files, root_dir_fd in iterator:
                    for name in files:
                        os.unlink(
                            name,
                            dir_fd=root_dir_fd,
                        )
                        logger.debug(
                            'deleted file %s in %s',
                            name,
                            root_dir,
                        )

                    for name in directories:
                        os.rmdir(
                            name,
                            dir_fd=root_dir_fd,
                        )
                        logger.debug(
                            'deleted directory %s in %s',
                            name,
                            root_dir,
                        )

                logger.info(
                    'emptied directory %s',
                    arguments.directory,
                )
        else:
            logger.info(
                'created directory %s',
                arguments.directory,
            )

        dir_fd = os.open(
            flags=os.O_DIRECTORY,
            path=arguments.directory,
        )

        allowed_entry_servers, allowed_exit_servers = build_allowed_server_lists(
            arguments,
        )

        ipv4_enabled = 'IPv4' in arguments.protocols
        if not ipv4_enabled:
            wireguard_peer_endpoint_ipv4_address = None

        ipv6_enabled = 'IPv6' in arguments.protocols
        if not ipv6_enabled:
            wireguard_peer_endpoint_ipv6_address = None

        for entry_server in allowed_entry_servers:
            entry_server_name = entry_server['name']

            logger.debug(
                'entry server: %s',
                entry_server_name,
            )

            basename = arguments.filename_prefix + entry_server_name

            if ipv4_enabled:
                wireguard_peer_endpoint_ipv4_address = entry_server['ipv4_addr_in']

            if ipv6_enabled:
                wireguard_peer_endpoint_ipv6_address = entry_server['ipv6_addr_in']

            writeout2(
                basename=basename,
                dir_fd=dir_fd,
                wireguard_peer_endpoint_ipv4_address=wireguard_peer_endpoint_ipv4_address,
                wireguard_peer_endpoint_ipv6_address=wireguard_peer_endpoint_ipv6_address,
                wireguard_peer_endpoint_port=51820,
                wireguard_peer_key=entry_server['public_key'],
            )

            basename = basename + '-'
            for exit_server in allowed_exit_servers:
                if exit_server != entry_server:
                    exit_server_name = exit_server['name']

                    logger.debug(
                        'multihopping: exit server: %s',
                        exit_server_name,
                    )

                    multihopping_basename = basename + exit_server_name

                    writeout2(
                        basename=multihopping_basename,
                        dir_fd=dir_fd,
                        wireguard_peer_endpoint_ipv4_address=wireguard_peer_endpoint_ipv4_address,
                        wireguard_peer_endpoint_ipv6_address=wireguard_peer_endpoint_ipv6_address,
                        wireguard_peer_endpoint_port=exit_server['multihop_port'],
                        wireguard_peer_key=exit_server['public_key'],
                    )

        os.close(
            fd=dir_fd,
        )

        exit_code = os.EX_OK
    else:
        logger.error(
            'The Python function `os.open` does not support the `dir_fd` parameter',
        )
        exit_code = os.EX_OSERR

    return exit_code


def build_allowed_server_lists(
            arguments,
        ):
    response = argbigga.mullvad.requests_session.get(
        'https://api.mullvad.net/public/relays/wireguard/v1/',
        timeout=10,
    )

    if response.ok:
        allowed_entry_servers = [
        ]
        allowed_exit_servers = [
        ]

        data = response.json(
        )

        countries = data['countries']
        for country in countries:
            country_code = country['code']
            country_name = country['name']

            cities = country['cities']
            for city in cities:
                city_code = city['code']
                city_name = city['name']

                servers = city['relays']
                for server in servers:
                    full_hostname = server['hostname']
                    hostname_must_be_stripped = full_hostname.endswith(
                        '-wireguard',
                    )
                    if hostname_must_be_stripped:
                        name = full_hostname[:-10]
                    else:
                        name = full_hostname
                    server['name'] = name

                    server_enabled_for_entry = (
                        (
                            not arguments.entry_countries
                            or
                            country_code in arguments.entry_countries
                            or
                            country_name in arguments.entry_countries
                        )
                        and
                        (
                            not arguments.entry_cities
                            or
                            city_code in arguments.entry_cities
                            or
                            city_name in arguments.entry_cities
                        )
                        and
                        (
                            not arguments.entry_servers
                            or
                            name in arguments.entry_servers
                        )
                    )
                    if server_enabled_for_entry:
                        allowed_entry_servers.append(
                            server,
                        )

                    server_enabled_for_exit = (
                        (
                            (
                                not arguments.exit_countries
                                and
                                not arguments.exit_cities
                                and
                                not arguments.exit_servers
                            )
                            and
                            arguments.multihopping
                        )
                        or
                        (
                            (
                                arguments.exit_countries
                                or
                                arguments.exit_cities
                                or
                                arguments.exit_servers
                            )
                            and
                            (
                                not arguments.exit_countries
                                or
                                country_code in arguments.exit_countries
                                or
                                country_name in arguments.exit_countries
                            )
                            and
                            (
                                not arguments.exit_cities
                                or
                                city_code in arguments.exit_cities
                                or
                                city_name in arguments.exit_cities
                            )
                            and
                            (
                                not arguments.exit_servers
                                or
                                name in arguments.exit_servers
                            )
                        )
                    )
                    if server_enabled_for_exit:
                        allowed_exit_servers.append(
                            server,
                        )

    return (
        allowed_entry_servers,
        allowed_exit_servers,
    )


def writeout2(
            basename,
            dir_fd,
            wireguard_peer_endpoint_ipv4_address,
            wireguard_peer_endpoint_ipv6_address,
            wireguard_peer_endpoint_port,
            wireguard_peer_key,
        ):
    if wireguard_peer_endpoint_ipv4_address:
        writeout(
            dir_fd=dir_fd,
            name=basename + '-ipv4',
            wireguard_peer_endpoint_host=wireguard_peer_endpoint_ipv4_address,
            wireguard_peer_endpoint_port=wireguard_peer_endpoint_port,
            wireguard_peer_key=wireguard_peer_key,
        )

    if wireguard_peer_endpoint_ipv6_address:
        writeout(
            dir_fd=dir_fd,
            name=basename + '-ipv6',
            wireguard_peer_endpoint_host='[' + wireguard_peer_endpoint_ipv6_address + ']',
            wireguard_peer_endpoint_port=wireguard_peer_endpoint_port,
            wireguard_peer_key=wireguard_peer_key,
        )


def writeout(
            dir_fd,
            name,
            wireguard_peer_endpoint_host,
            wireguard_peer_endpoint_port,
            wireguard_peer_key,
        ):
    filename = name + '.conf'

    fd = os.open(
        dir_fd=dir_fd,
        flags=os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        mode=stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH,
        path=filename,
    )
    file = os.fdopen(
        fd=fd,
        mode='w',
    )

    argbigga.wireguard.serialize_configuration(
        file=file,
        peer_endpoint_host=wireguard_peer_endpoint_host,
        peer_endpoint_port=wireguard_peer_endpoint_port,
        peer_key=wireguard_peer_key,
    )

    file.close(
    )
