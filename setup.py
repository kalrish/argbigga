import setuptools


packages = setuptools.find_packages(
    where='src',
)

"""
In Swedish, a «mullvad» is a mole, an appropriate image for a VPN service concerned with privacy.
Meanwhile, «argbigga» stands for «shrew», the mole's closest relative.
In this spirit, argbigga the command-line tool is a companion to Mullvad's own.

This tool is neither developed nor endorsed by the team behind Mullvad or Mullvad's parent company, Amagicom AB.
"""

setuptools.setup(
    author='David Joaquín Shourabi Porcel',
    author_email='david@djsp.eu',
    description='command-line tool to help automate Mullvad VPN setups on Linux',
    entry_points={
        'console_scripts': [
            'argbigga = argbigga.cli.main:entry_point',
        ],
    },
    install_requires=[
        'requests >= 2.22.0',
    ],
    long_description=__doc__,
    maintainer='David Joaquín Shourabi Porcel',
    maintainer_email='david@djsp.eu',
    name='argbigga',
    packages=packages,
    package_dir={
        '': 'src',
    },
    python_requires='>= 3.9.0',
    url='https://github.com/wgnetns/argbigga',
    version='1.0.0',
)
