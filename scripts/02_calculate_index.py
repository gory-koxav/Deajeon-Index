# 필요한 라이브러리가 없다면 설치해주세요.
# pip install pandas matplotlib tqdm holidayskr

import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
from holidayskr import is_holiday
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import glob

# --- 설정 변수 ---
# ticker.py 파일이 같은 디렉토리에 있다고 가정합니다.
# 만약 없다면 아래 ticker 리스트를 직접 사용하세요.
try:
    from ticker import tickers
except ImportError:
    print("경고: ticker.py 파일을 찾을 수 없어 기본 티커 목록을 사용합니다.")
    tickers = [
        '287840', '435570', '475830', '475960', '044990', '457370', '469750', '431190', '460470', '452200',
        '360350', '452190', '338840', '451760', '372320', '417010', '405000', '363250', '277810', '368770',
        '335810', '348350', '318410', '336570', '226330', '256150', '253840', '228760', '208340', '269620',
        '214430', '087010', '187420', '208370', '196170', '105550', '171120', '141080', '143160', '064290',
        '099320', '092070', '065150', '092730', '064550', '082210', '082270', '069540', '072020', '060380',
        '054800', '046210', '023760'
    ]

OHLCV_DIR = './data/ohlcv'
MARCAP_DIR = './data/marcap'
DEAJEON_INDEX_DIR = './data/deajeon_index'
os.makedirs(DEAJEON_INDEX_DIR, exist_ok=True)

# 한글 폰트 설정 (Windows: Malgun Gothic, macOS: AppleGothic)
# 자신의 운영체제에 맞는 폰트 이름을 사용하세요.
try:
    font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    plt.rc('font', family=font_name)
except FileNotFoundError:
    try:
        plt.rc('font', family='AppleGothic')
    except:
        print("경고: 한글 폰트를 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지

def load_all_data(start_date, end_date):
    """
    지정된 기간 동안 모든 티커의 ohlcv 및 시가총액 데이터를 불러와 병합합니다.
    - 파일명의 날짜를 직접 파싱하여 가장 최신 파일을 로드합니다.
    - 로드하는 파일의 날짜가 오늘 날짜와 다를 경우 경고 메시지를 출력합니다.
    """
    all_data_list = []
    print("데이터 로딩 중...")
    
    today_yyyymmdd = datetime.now().strftime("%Y%m%d")

    # 파일 경로에서 날짜(YYYYMMDD)를 추출하는 헬퍼 함수
    def get_date_from_path(path):
        try:
            # 파일 이름(e.g., ohlcv_287840_..._20250619.csv)에서 마지막 '_' 뒤의 부분을 추출
            date_str = os.path.basename(path).split('_')[-1].replace('.csv', '')
            return date_str
        except IndexError:
            # 파일 형식이 예상과 다를 경우
            return None

    for ticker in tqdm(tickers):
        # 해당 티커의 모든 ohlcv, marcap 파일 목록 가져오기
        ohlcv_files = glob.glob(os.path.join(OHLCV_DIR, f'ohlcv_{ticker}_*.csv'))
        marcap_files = glob.glob(os.path.join(MARCAP_DIR, f'marcap_{ticker}_*.csv'))
        
        if not ohlcv_files or not marcap_files:
            print(f"경고: {ticker}에 대한 데이터 파일을 찾을 수 없습니다.")
            continue
        
        # --- 여기가 수정된 핵심 로직입니다 ---
        # 1. 날짜를 기준으로 가장 최신 파일을 선택
        latest_ohlcv_file = max(ohlcv_files, key=get_date_from_path)
        latest_marcap_file = max(marcap_files, key=get_date_from_path)
        
        # 2. 선택된 파일의 날짜가 오늘 날짜와 다른지 확인하고 경고 출력
        ohlcv_file_date = get_date_from_path(latest_ohlcv_file)
        if ohlcv_file_date != today_yyyymmdd:
            print(f"경고 (OHLCV): {ticker}의 로드된 파일 날짜({ohlcv_file_date})가 오늘({today_yyyymmdd})과 다릅니다. 파일: {os.path.basename(latest_ohlcv_file)}")
            
        marcap_file_date = get_date_from_path(latest_marcap_file)
        if marcap_file_date != today_yyyymmdd:
            print(f"경고 (Marcap): {ticker}의 로드된 파일 날짜({marcap_file_date})가 오늘({today_yyyymmdd})과 다릅니다. 파일: {os.path.basename(latest_marcap_file)}")
        
        try:
            # 가장 최신 파일 로드
            df_ohlcv = pd.read_csv(latest_ohlcv_file)
            df_marcap = pd.read_csv(latest_marcap_file)
            
            # 두 데이터프레임을 '날짜' 기준으로 병합
            df_merged = pd.merge(df_ohlcv, df_marcap, on='날짜', how='inner')
            df_merged['ticker'] = ticker
            all_data_list.append(df_merged)

        except Exception as e:
            print(f"에러: {ticker} 파일 처리 중 오류 발생 - {e}")

    if not all_data_list:
        print("에러: 처리할 데이터가 없습니다. 스크립트를 종료합니다.")
        return pd.DataFrame()

    # 모든 데이터를 하나의 데이터프레임으로 합치기
    full_df = pd.concat(all_data_list, ignore_index=True)
    full_df['날짜'] = pd.to_datetime(full_df['날짜'])
    
    # 지정된 기간으로 데이터 필터링
    full_df = full_df[(full_df['날짜'] >= start_date) & (full_df['날짜'] <= end_date)].copy()
    full_df.sort_values(by=['날짜', 'ticker'], inplace=True)
    
    return full_df

def calculate_initial_index(df_base):
    """
    최초 인덱스와 기준 시가총액을 계산합니다.
    - 기준일의 모든 종목의 시가총액 합을 기준 시가총액으로 설정합니다.
    - 최초 인덱스 값은 100으로 설정합니다.
    """
    base_market_cap = df_base['시가총액'].sum()
    base_index = 100.0
    return base_index, base_market_cap

def calculate_deajeon_index(current_market_cap, base_market_cap, base_index=100.0):
    """
    현재 시가총액을 바탕으로 deajeon_index를 계산합니다.
    공식: 현재 인덱스 = 기준 인덱스 * (현재 시가총액 합 / 기준 시가총액 합)
    """
    if base_market_cap == 0:
        return base_index
    return base_index * (current_market_cap / base_market_cap)

def main():
    """메인 실행 함수"""
    # 1. 대상 날짜 설정
    today = datetime.now()
    two_years_ago = today - timedelta(days=730) # 2년전
    two_years_ago = datetime(2025, 1, 1)
    
    print(f"분석 기간: {two_years_ago.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")

    # 모든 데이터를 한번에 로드
    all_stock_data = load_all_data(two_years_ago, today)
    if all_stock_data.empty:
        return

    # 데이터가 존재하는 실제 시작일 찾기
    first_data_date = all_stock_data['날짜'].min()
    print(first_data_date, type(first_data_date))

    # first_data_date = pd.Timestamp('2020-01-02 00:00:00')
    print(f"데이터가 존재하는 가장 빠른 날짜: {first_data_date.strftime('%Y-%m-%d')}")
    
    # 4. 최초 인덱스 산출
    df_base = all_stock_data[all_stock_data['날짜'] == first_data_date]
    base_index, base_market_cap = calculate_initial_index(df_base)
    
    print(first_data_date, type(first_data_date))
    print(f"기준일: {first_data_date.strftime('%Y-%m-%d')}")
    print(f"기준 시가총액: {base_market_cap:,.0f} 원")
    print(f"기준 deajeon_index: {base_index}")
    
    # 인덱스 계산 및 특이사항 기록 준비
    date_range = pd.date_range(start=first_data_date, end=today)
    deajeon_index_results = []
    
    # 각 티커의 첫 거래일 기록
    first_appearance = all_stock_data.groupby('ticker')['날짜'].min().to_dict()

    print("\ndeajeon_index 계산 및 특이사항 확인 시작...")
    for current_date in tqdm(date_range):
        log_message = []
        is_hday = is_holiday(current_date.strftime('%Y-%m-%d'))
        
        # 현재 날짜의 데이터 필터링
        daily_data = all_stock_data[all_stock_data['날짜'] == current_date]
        
        # --- 시가총액 저장을 위한 변수 초기화 ---
        market_cap_for_day = None

        # 3. 공휴일 데이터 존재 여부 확인
        if is_hday:
            if not daily_data.empty:
                tickers_on_holiday = ', '.join(daily_data['ticker'].unique())
                log_message.append(f"공휴일에 다음 티커의 데이터가 존재: {tickers_on_holiday}")
            
            # 결과 저장 및 다음 날짜로 이동
            deajeon_index_results.append({
                "날짜": current_date,
                "deajeon_index": None,
                "시가총액": None, # (수정) 공휴일은 시가총액도 None
                "특이사항": ' '.join(log_message) if log_message else "공휴일"
            })
            continue

        # 5. deajeon_index 산출 (공휴일이 아닌 경우)
        if not daily_data.empty:
            current_market_cap = daily_data['시가총액'].sum()
            market_cap_for_day = current_market_cap # (수정) 계산된 시가총액 저장
            index_value = calculate_deajeon_index(current_market_cap, base_market_cap, base_index)
        else:
            # 데이터가 없으면 이전 값 유지
            if deajeon_index_results:
                last_valid_index = next((res['deajeon_index'] for res in reversed(deajeon_index_results) if pd.notna(res['deajeon_index'])), None)
                index_value = last_valid_index
            else:
                index_value = base_index

        # 6. 상장 이후 데이터 누락 확인
        present_tickers = set(daily_data['ticker'])
        for ticker, start_date in first_appearance.items():
            if current_date >= start_date and ticker not in present_tickers:
                log_message.append(f"데이터 누락: {ticker}")
        
        # --- (수정) 최종 결과 저장 시 '시가총액' 컬럼 추가 ---
        deajeon_index_results.append({
            "날짜": current_date,
            "deajeon_index": index_value,
            "시가총액": market_cap_for_day, # '시가총액' 키와 값 추가
            "특이사항": ' '.join(log_message)
        })

    # 7. CSV로 저장
    df_result = pd.DataFrame(deajeon_index_results)
    
    # --- (수정) deajeon_index와 시가총액 모두 이전 값으로 채우기 ---
    df_result['deajeon_index'] = df_result['deajeon_index'].ffill()
    df_result['시가총액'] = df_result['시가총액'].ffill() 
    
    today_str = today.strftime("%Y%m%d")
    csv_path = os.path.join(DEAJEON_INDEX_DIR, f'deajeon_index_{today_str}.csv')
    df_result.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n인덱스 계산 완료! 결과가 '{csv_path}'에 저장되었습니다.")

    # 8. 시각화하여 저장
    plt.figure(figsize=(15, 7))
    plt.plot(df_result['날짜'], df_result['deajeon_index'], label='deajeon_index', color='royalblue')
    plt.title('Deajeon Index (대전 인덱스) 추이', fontsize=16)
    plt.xlabel('날짜', fontsize=12)
    plt.ylabel('인덱스', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    plot_path = os.path.join(DEAJEON_INDEX_DIR, f'deajeon_index_{today_str}.png')
    plt.savefig(plot_path)
    print(f"인덱스 그래프가 '{plot_path}'에 저장되었습니다.")
    # plt.show() # 로컬에서 직접 실행 시 그래프를 보려면 이 줄의 주석을 해제하세요.

if __name__ == '__main__':
    main()