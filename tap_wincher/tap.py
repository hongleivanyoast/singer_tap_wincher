import logging
from argparse import Namespace

import pkg_resources
from singer import get_logger, utils
from singer.catalog import Catalog

from tap_wincher.wincher import Wincher
from tap_wincher.discover import discover
from tap_wincher.sync import sync

VERSION: str = pkg_resources.get_distribution('tap-wincher').version
LOGGER: logging.RootLogger = get_logger()
REQUIRED_CONFIG_KEYS: list = [
    "username",
    "password",
    "start_date",
]

@utils.handle_top_exception(LOGGER)
def main() -> None:
    """run tap."""
    # Parse command line arguments
    args: Namespace = utils.parse_args(REQUIRED_CONFIG_KEYS)

    LOGGER.info(f'>>> Running tap-wincher v{VERSION}')

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog: Catalog = discover()
        catalog.dump()
        return
    # Otherwise run in sync mode
    
    if args.catalog:
        catalog = args.catalog
    else:
        catalog = discover()
    
    #Initialize postmark client
    wincher: Wincher = Wincher(
        args.config['username'],args.config['password'],
    )
    sync(wincher, args.state, catalog, args.config['start_date'])
   

if __name__=='__main__':
    main()



