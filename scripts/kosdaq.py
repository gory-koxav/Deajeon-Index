import os
import time
from datetime import datetime, timedelta
from tqdm import tqdm
from pykrx import stock
from pykrx import bond

OHLCV_DIR = './data/kosdaq'
MARCAP_DIR = './data/kosdaq'
os.makedirs(OHLCV_DIR, exist_ok=True)
os.makedirs(MARCAP_DIR, exist_ok=True)

today = datetime.now()
today_yyyymmdd = today.strftime("%Y%m%d")
two_years_ago = today.replace(year=today.year - 50)
two_years_later_yyyymmdd = two_years_ago.strftime("%Y%m%d")

print(f"오늘 날짜 (yyyymmdd): {today_yyyymmdd}")
print(f"2년전 날짜 (yyyymmdd): {two_years_later_yyyymmdd}")


# for ticker in tqdm(tickers):
tickers = stock.get_index_ticker_list(market='KOSDAQ')
ticker = tickers[0]
# get ticker name
company_name = stock.get_index_ticker_name(ticker)

# get OHLCV
ohlcv_filename = f"ohlcv_{ticker}_{company_name}_{today_yyyymmdd}.csv"
ohlcv_filepath = os.path.join(OHLCV_DIR, ohlcv_filename)
df_ohlcv = stock.get_index_ohlcv(two_years_later_yyyymmdd, today_yyyymmdd, ticker)
# save OHLCV
if not os.path.exists(ohlcv_filepath):
    df_ohlcv.to_csv(ohlcv_filepath, mode='w')
else:
    df_ohlcv.to_csv(ohlcv_filepath, mode='a', header=False)

time.sleep(1)

# # get MARCAP
# marcap_filename = f'marcap_{ticker}_{company_name}_{today_yyyymmdd}.csv'
# marcap_filepath = os.path.join(MARCAP_DIR, marcap_filename)
# df_marcap = stock.get_market_cap(two_years_later_yyyymmdd, today_yyyymmdd, ticker)
# # save MARCAP
# if not os.path.exists(marcap_filepath):
#     df_marcap.to_csv(marcap_filepath, mode='w')
# else:
#     df_marcap.to_csv(marcap_filepath, mode='a', header=False)

# time.sleep(1)