import logging
from datetime import date, datetime, timedelta
from types import MappingProxyType
from typing import Callable, List, Generator
import httpx

import singer 
from dateutil.rrule import DAILY, rrule

from tap_wincher.cleaners import CLEANERS
LOGGER: logging.RootLogger = singer.get_logger()



API_SCHEME: str = "https://"
API_BASE_URL: str = 'api.wincher.com'
API_REVENUE_PATH: str = '/beta/commission/yoast/'
API_DATE_PATH: str = ':date:'

HEADERS: MappingProxyType = MappingProxyType({  # Frozen dictionary
    'Accept': 'application/json',
    'username': ':user:',
    'password': ':pass:',
})


class Wincher(object):
    def __init__(
        self,
        username: str,
        password: str,
    ) -> None:  # noqa: DAR101
        """Initialize client.

        Arguments:
            username {str} -- Wincher username
            password {str} -- Wincher password
        """
        self.username: str = username
        self.password: str = password
        self.logger: logging.Logger = singer.get_logger()
        self.client: httpx.Client = httpx.Client(http2=True)

    def wincher(  # noqa: WPS210, WPS432
        self,
        **kwargs: dict,
    ) -> Generator[dict, None, None]:  # noqa: DAR101
        """Get all bounce reasons from date.

        Raises:
            ValueError: When the parameter start_date is missing

        Yields:
            Generator[dict] --  Cleaned wincher Data
        """
        # Validate the start_date value exists
        start_date_input: str = str(kwargs.get('start_date', ''))

        if not start_date_input:
            raise ValueError('The parameter start_date is required.')

        #get the Cleaner
        cleaner: Callable = CLEANERS.get('wincher',{})


        # Create Header with Auth Token
        self._create_headers()

        for date_day in self._start_days_till_now(start_date_input):

            # Replace placeholder in reports path
            from_to_date: str = API_DATE_PATH.replace(
                ':date:',
                date_day.split('-')[0]+ date_day.split('-')[1],
            )

            self.logger.info(
                f'Recieving wincher data from {date_day}'
            )

            # Build URL
            url: str = (
                f'{API_SCHEME}{API_BASE_URL}{API_REVENUE_PATH}'
                f'{from_to_date}'
            )

            # Make the call to Postmark API
            response: httpx._models.Response = self.client.get(  # noqa: WPS437
                url,
                auth = (self.username, self.password),
                headers=self.headers,
            )

            # Raise error on 4xx and 5xxx
            response.raise_for_status()

            # Create dictionary from response
            response_data: dict = response.json()

            # Yield Cleaned results
            yield cleaner(date_day, response_data)

    def _create_headers(self) -> None:
        """Create authentication headers for requests"""
        headers: dict = dict(HEADERS)
        headers['username'] =  headers['username'].replace(':user:',self.username,)
        headers['password'] =  headers['password'].replace(':pass:',self.password,)
        self.headers = headers

    def _start_days_till_now(self, start_date: str)->Generator:
        """Yield YYYY/MM/DD for every day until now.
        Arguments:
            start_date {str} -- Start date e.g. 2020-01-01
        Yields:
            Generator -- Every day until now.
        """
        #parse input date
        year: int = int(start_date.split('-')[0])
        month: int = int(start_date.split('-')[1].lstrip())
        day: int = int(start_date.split('-')[2].lstrip())

         # Setup start period
        period: date = date(year, month, day)

        # Setup itterator
        dates: rrule = rrule(
            freq=DAILY,
            dtstart=period,
            until=datetime.utcnow(),
        )

        # Yield dates in YYYY-MM-DD format
        yield from (date_day.strftime('%Y-%m-%d') for date_day in dates)