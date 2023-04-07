import requests
from backend.utils import fxsymbol, pickle_it
import pandas as pd
import os
import logging
from datetime import datetime
from dateutil import parser
from backend.decorators import MWT
from backend.config import load_config
from backend.parseNumbers import parseNumber


@MWT(timeout=600)
def apikey(source, required=True):

    API_KEY = None
    if source == 'cryptocompare':
        return "460e0cd0b6e51831a3ba154a60862edf28d97e0fdc1b9f84591957c6e8bfd3d6"

        # cbe800c80a3fe9c47d68aa8b94461f5e5220641a23010bb6ef4883fd7f4193a6
        # b826b0e06b4ebb7a230b9aecfc49cda0d3d15534e409328f0930e5183a9e796e
        # 4b0d5a0db42e77272b7bfb37dfa406c374e9fc67a43070c764912023ae2b73ea
        # f2947f57bae7e3fde9a05d658ebe74e3516ec3da28457b9f56a9010aad7471fe
        # 460e0cd0b6e51831a3ba154a60862edf28d97e0fdc1b9f84591957c6e8bfd3d6
        # fa890fedfc79ee4d0cac355fd5e00d5771e6c5d91224b63b6bad5aa547a36d34
        # 841101269cff0ea7b96ba41eedcb62754e1c40a20b511d794f4ee3c13a3a6de2
        # 4f1e4588c990bf05ba436e794729a897390a4ff5d46a7c9a8e1547b397205a30
        # 415b4528535c017c4bb678f1b1470a84025f252328d9b1fa3393139202de315b
        # 9863dbe4217d98738f4ab58137007d24d70da92031584ba31de78137e0576225
        # a26f396ec9106a68ea618f62ee96aa357d31c0568c34ce974ccefcda6700e69a
        # ec2b8cbd529690ce15b5eca76e59b470e79e68f4b876d308d06a91afae2e7a78
        # 39667965c99dfa9f5c3c368867ae776e019f46275fcba2d1d3fe3e04812842e1


        # Check if a cryptocompare key is stored at home directory
        API_KEY = pickle_it('load', 'cryptocompare_api.pkl')
        if "\n" in API_KEY:
            API_KEY = API_KEY.strip("\n")
        if API_KEY != 'file not found':
            return API_KEY

    if source == 'alphavantage':
        # Use a standard API Key - WARNING this
        # will result in a daily limit of calls
        # if many users start using this key
        API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

    if source == 'fmp':
        API_KEY = os.getenv('FMP_API_KEY')

    if source == 'twelvedata':
        API_KEY = os.getenv('TWELVE_DATA_API_KEY')

    # Let's try to load from config.ini
    if API_KEY is None:
        try:
            config = load_config()
            API_KEY = config['API'][source]
        except Exception:
            API_KEY = None

    if required and API_KEY is None:
        raise Exception(f'{source} requires an API KEY and none was found.')
    return API_KEY


def price_ondate(ticker, date_input, source=None):
    df = historical_prices(ticker, source=source)
    if df.empty:
        return None
    try:
        dt = pd.to_datetime(date_input)
        df.index = df.index.astype('datetime64[ns]')
        df = df[~df.index.duplicated(keep='first')]
        idx = df.iloc[df.index.get_indexer([dt], method='nearest')]
        return (idx)
    except Exception as e:
        print("Error getting price on date " + str(date_input) + " for " +
                        str(ticker) + ". Error " + str(e))
        return (None)


# The below is a priority list for some usually accessed tickers
mapping = {
    'OIL': ['fmp', 'twelvedata', 'alphavantage_global'],
    'QQQ': ['twelvedata', 'fmp', 'yahoo'],
    'BTC': ['cryptocompare', 'alphavantage_currency'],
    'GBTC': ['twelvedata', 'fmp', 'alphavantage_global', 'yahoo'],
    'ETH': ['cryptocompare', 'alphavantage_currency'],
    'MSTR': ['alphavantage_global', 'twelvedata', 'fmp', 'yahoo'],
    'FBTC.TRT': ['alphavantage_global', 'twelvedata', 'fmp', 'yahoo'],
}


def historical_prices(ticker, fx='USD', source=None):
    '''
    RETURNS a DF with
        columns={
                'close': 'close',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'volume': 'volume'
        }
    '''

    ticker = ticker.replace(' ', '')
    ticker = ticker.upper()

    if source and type(source) != list:
        raise TypeError(
            "source has to be a list of strings - can be one string inside a list"
        )

    try:
        source_list = mapping[ticker]
    except KeyError:
        source_list = [
            'cryptocompare'
        ]

    from pricing_engine.cryptocompare import historical as cc_historical

    results = pd.DataFrame()
    filename = (ticker + "_" + fx + ".price")

    # Gets from each source
    for src in source_list:
        # Try to load file if exists
        # Check if file was updated today
        from backend.config import home_dir
        file_check = os.path.join(home_dir, filename)
        # Try to read from file and check how recent it is
        try:
            today = datetime.now().date()
            filetime = datetime.fromtimestamp(os.path.getctime(file_check))
            if filetime.date() == today:
                df = pd.read_pickle(file_check)
            return (df)
        except Exception as e:
            pass

        if src == 'cryptocompare':
            results = cc_historical(ticker)
            try:
                if results == 'API_LIMIT':
                    print("API LIMIT REACHED. RESTART.")
                    return None
            except Exception:
                pass

        # convert index to datetime
        results.index = pd.to_datetime(results.index)
        # remove duplicates
        results = results.loc[~results.index.duplicated(keep='first')].copy()
        # Check if data is valid
        if not results.empty:
            # Include fx column and convert to currency if needed
            if fx != 'USD':
                # Get a currency df
                df_fx = aa_historical(fx, function='FX_DAILY')
                df_fx.index = pd.to_datetime(df_fx.index)
                df_fx = df_fx.loc[~df_fx.index.duplicated(keep='first')]
                df_fx = df_fx.rename(columns={'close': 'fx_close'})
                df_fx = df_fx[['fx_close']]
                df_fx['fx_close'] = pd.to_numeric(df_fx.fx_close,
                                                  errors='coerce')
                df_fx['fx_close'] = 1 / df_fx['fx_close']
                # Merge the two dfs:
                merge_df = pd.merge(results, df_fx, on='date', how='inner')
                merge_df['close'] = merge_df['close'].astype(float)
                merge_df['close_converted'] = merge_df['close'] * merge_df[
                    'fx_close']
                results = merge_df.copy()

            else:
                results['fx_close'] = 1
                results['source'] = src
                results['close_converted'] = pd.to_numeric(results.close,
                                                           errors='coerce')

            results.index = results.index.astype('datetime64[ns]')
            # sort results by index
            results = results.sort_index(ascending=True)

            # Save this file to be used during the same day instead of calling API
            pickle_it(action='save', filename=filename, data=results)
            # save metadata as well
            metadata = {'source': src, 'last_update': datetime.utcnow()}
            filemeta = (ticker + "_" + fx + ".meta")
            pickle_it(action='save', filename=filemeta, data=metadata)
            print(f"Successfully saved: {ticker}")
            return (results)
        else:
            logging.info(
                f"Source {src} does not return any data for {ticker}. Trying other sources."
            )
    if results.empty:
        pickle_it(action='save', filename=filename, data=results)
        # # save metadata as well
        metadata = {'source': src, 'last_update': datetime.utcnow()}
        filemeta = (ticker + "_" + fx + ".meta")
        pickle_it(action='save', filename=filemeta, data=metadata)
        logging.warning(
            f"Could not retrieve a df for {ticker} from any source")
    return (results)


def realtime_price(ticker, fx=None, source=None, parsed=True):
    '''
    Gets realtime price from first provider available and returns
    result = {
            'symbol': ,
            'name': ,
            'price': ,
            'fx': ,
            'time': ,
            'timezone':
            'source':
        }
    '''
    if fx is None:
        fx = 'USD'

    if fx == 'USD':
        fxrate = 1
    else:
        from pricing_engine.alphavantage import realtime as aa_realtime
        fxrate = aa_realtime(fx)
        fxrate = parseNumber(fxrate['price'])

    ticker = ticker.replace(' ', '')
    if source and type(source) != list:
        raise TypeError(
            "source has to be a list of strings - can be one string inside a list"
        )

    try:
        source_list = mapping[ticker]
    except KeyError:
        source_list = [
            'cryptocompare', 'alphavantage_currency', 'alphavantage_global',
            'twelvedata', 'fmp'
        ]

    from pricing_engine.cryptocompare import realtime as cc_realtime

    results = None
    # Gets from each source
    for src in source_list:
        if src == 'alphavantage_currency':
            results = aa_realtime(ticker,
                                  'USD',
                                  'CURRENCY_EXCHANGE_RATE',
                                  parsed=parsed)
        if src == 'cryptocompare':
            results = cc_realtime(ticker, 'USD', parsed=parsed)

        # Check if data is valid
        if results is not None:
            if parsed and 'price' in results:
                if results['price'] is not None:
                    if isinstance(results['time'], str):
                        results['time'] = parser.parse(results['time'])
                    results['price'] = parseNumber(results['price'])
                    results['price'] = (results['price'] / fxrate)
                    return (results)
    return (results)


def GBTC_premium(price):
    # Calculates the current GBTC premium in percentage points
    # to BTC (see https://grayscale.com/products/grayscale-bitcoin-trust/)
    SHARES = 0.00091347  # as of 12/10/2022
    fairvalue = realtime_price("BTC")['price'] * SHARES
    premium = (price / fairvalue) - 1
    return fairvalue, premium


def get_ticker_info(ticker, src, exactmatch=True):
    if src == 'twelvedata':
        # Result of this info from source:
        # [{
        #     'symbol': 'GBTC',
        #     'name': 'Grayscale Bitcoin Trust (BTC)',
        #     'provider': '12Data',
        #     'notes': 'OTC',
        #     'fx': 'USD'
        # }]
        from pricing_engine.twelvedata import asset_list
        data = asset_list(ticker)
    elif src == 'alphavantage' or src == 'alphavantage_global':
        # [{
        #     'symbol': 'GBTC',
        #     'name': 'Grayscale Investments LLC',
        #     'provider': 'aa_stock',
        #     'notes': 'ETF United States',
        #     'fx': 'USD'
        # }]
        from pricing_engine.alphavantage import asset_list
        data = asset_list(ticker)
    elif src == 'cryptocompare':
        # [{
        #     'symbol': 'GBTC',
        #     'name': 'GigTricks (GBTC)',
        #     'provider': 'cc_digital',
        #     'fx': 'USD',
        #     'notes': 'Digital Currency'
        # }]
        from pricing_engine.cryptocompare import asset_list
        data = asset_list(ticker)
    elif src == 'fmp':
        # data = [{
        #     'symbol': 'SPBC',
        #     'name': 'Simplify U.S. Equity PLUS GBTC ETF',
        #     'provider': 'fp_stock',
        #     'notes': 'NASDAQ',
        #     'fx': 'USD'
        # }]
        from pricing_engine.fmp import asset_list
        data = asset_list(ticker)

    elif src == 'yahoo':
        # data = [{
        #     'symbol': 'SPBC',
        #     'name': 'Simplify U.S. Equity PLUS GBTC ETF',
        #     'provider': 'fp_stock',
        #     'notes': 'NASDAQ',
        #     'fx': 'USD'
        # }]
        from pricing_engine.yfinance import asset_list
        data = asset_list(ticker)

    # Keep only the results that have the same ticker as inputed ticker
    if exactmatch is True:
        for element in data:
            if element['symbol'] != ticker:
                data.remove(element)

    return data


def fx_rate():
    config = load_config()
    fx = config['PORTFOLIO']['base_fx']

    # This grabs the realtime current currency conversion against USD
    try:
        rate = {}
        rate['base'] = fx
        rate['symbol'] = fxsymbol(fx)
        rate['name'] = fxsymbol(fx, 'name')
        rate['name_plural'] = fxsymbol(fx, 'name_plural')
        rate['cross'] = "USD" + " / " + fx
        if fx.upper() == 'USD':
            rate['fx_rate'] = 1
        else:
            try:
                from pricing_engine.alphavantage import realtime as aa_realtime
                fxrate = aa_realtime(fx)
                fxrate = parseNumber(fxrate['price'])
                rate['fx_rate'] = 1 / fxrate
            except Exception as e:
                rate['error'] = ("Error: " + str(e))
                rate['fx_rate'] = 1
    except Exception as e:
        rate = {}
        rate['error'] = ("Error: " + str(e))
        rate['fx_rate'] = 1
    return (rate)


def fx_price_ondate(base, cross, date):
    # Gets price conversion on date between 2 currencies
    # on a specific date
    try:
        if base == 'USD':
            price_base = 1
        else:
            base_class = price_ondate(base, date)
            price_base = base_class['close']
        if cross == 'USD':
            price_cross = 1
        else:
            cross_class = price_ondate(cross, date)
            price_cross = cross_class['close']
        conversion = float(price_base) / float(price_cross)
        return (conversion)
    except Exception:
        return (1)


# Thread to download data
def download_data(tickers):
    import threading

    def createNewDownloadThread(ticker):
        download_thread = threading.Thread(
            target=historical_prices,
            args=(ticker, 'USD', ['cryptocompare']))
        download_thread.start()

    for ticker in tickers:
        # createNewDownloadThread(ticker)
        historical_prices(ticker, 'USD', ['cryptocompare'])