import pkg_resources

distribution = pkg_resources.get_distribution(
    'argbigga',
)
version = distribution.version
