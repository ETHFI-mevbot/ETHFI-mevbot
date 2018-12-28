import requests


class PublicClient(object):
    """Ethfinex public client API."""

    def __init__(self, api_url='https://api.ethfinex.com/v2'):
        """Create Ethfinex API public client.

        Args:
            api_url (Optional[str]): API URL. Defaults to etfhinex API.
        """
        self.url = api_url.rstrip('/')
        self.auth = None
        self.session = requests.Session()

    def get_platform_status(self):
        """Get the current status of the platform.
        Returns:
            1=operative
            0=maintenance
        """
        return self._send_message('/platform/status')

    def get_ticker(self, pair):
        """Get a list of available currency pairs for trading.

        Args:
            pair (str): Name of the pair.
        Returns:
            [
                BID,
                BID_SIZE,
                ASK,
                ASK_SIZE,
                DAILY_CHANGE,
                DAILY_CHANGE_PERC,
                LAST_PRICE,
                VOLUME,
                HIGH,
                LOW
            ]
        """
        return self._send_message(f'/ticker/{pair}')

    def get_trades(self, pair, limit=None, start=None, end=None, sort=None):
        """Get all the pertinent details of the trade, such as price, size and
        time.

        Args:
            pair (str): Name of the pair.
            limit (Optional[int]): Number of records.
            start (Optional[int]): Milisecond start time.
            end (Optional[int]): Milisecond end time.
            sort (Optional[int]): if = 1 sorts results returned with old > new

        Returns:
        [
            [
                ID,
                MTS,
                AMOUNT,
                PRICE
            ]
        ]
        """
        params = {}
        if limit:
            params['limit'] = limit
        if start and end and start < end:
            params['start'] = start
            params['end'] = end
        else:
            raise ValueError('The start time cannot be after the end time.')
        if sort:
            params['sort'] = sort
        return self._send_message(f'/trades/{pair}/hist', params=params)

    def get_books(self, pair, precision, len=None):
        """Get the state of the Bitfinex order book. It is provided on a price
        aggregated basis, with customizable precision.

        TODO: Clearly deefine precision and len

        Args:
            pair (str): Name of the pair.
            precision (str): Level of price aggregation(P0, P1, P2, P3, P4, R0)
            sort (Optional[int]): if = 1 sorts results returned with old > new
            len (Optional[int]): Number of price points ("25", "100")

        Returns:
        [
            [
                PRICE,
                COUNT,
                AMOUNT
            ]
        ]
        """
        params = {}
        accepted_len = [25, 100]
        if len and len in accepted_len:
            params['len'] = len
            return self._send_message(f'/book/{pair}/{precision}', params=params)
        elif len and len not in accepted_len:
            raise ValueError('The len can only be 25 or 100.')

        return self._send_message(f'/book/{pair}/{precision}')

    # TODO: Include 'side' for the 'pos.size' calls.
    def get_stats(self, symbol, key, size, side, section, sort=None):
        """Various statistics about the requested pair.

        TODO: Clearly define params.
        The `key` param descriptions are as follows:
        1. funding.size = Total Active Funding
        2. credits.size = Active Funding used in positions
        3. credits.size.sym = Active Funding used in positions (per symbol)
        4. pos.size = Total Open Position (long / short)

        **Note**: The Ethfinex API has a parameter for `side`, which can be
        'short' or 'long'. When calling the API on their site, this parameter
        is not used, so it will not be used here.

        Args:
            symbol (str): Name of the symbol.
            key (str): Allowed values: "funding.size", "credits.size",
                       "credits.size.sym", "pos.size"
            size (str): Available values: '1m'
            section (str): Available values: "last", "hist"
            sort (Optional[int]): Either 0 or 1. If = 1 it sorts results
                                  returned with old > new

        Returns:
            [
                [ MTS, VALUE ],
                ...
            ]
        """
        params = {}
        if sort == 1:
            params['sort'] = 1
            return self._send_message(f'/stats1/{key}:{size}:{symbol}/{section}',
                                      params=params)

        return self._send_message(f'/stats1/{key}:{size}:{symbol}/{section}')

    def _send_message(self, endpoint, params=None, data=None):
        """Send API request.

        Args:
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST
        """
        url = self.url + endpoint
        r = self.session.request('get', url, params=params, data=data,
                                 auth=self.auth, timeout=30)
        return r.json()
