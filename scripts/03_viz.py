import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

def read_korean_csv(file_path):
    """
    한글 CSV 파일의 인코딩을 자동으로 찾아 읽어주는 함수.
    """
    encodings_to_try = ['cp949', 'euc-kr', 'utf-8-sig', 'utf-8']
    
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df
        except (UnicodeDecodeError, FileNotFoundError):
            continue
            
    print(f"❌ '{file_path}' 파일 읽기에 실패했습니다. 경로를 확인해주세요.")
    return None

def visualize_normalized(deajeon_df, kosdaq_df, start_date, end_date, output_path):
    """
    그래프 1: 두 지수를 정규화하여 상대적 성과를 비교하는 그래프를 생성합니다.
    """
    deajeon_base = deajeon_df.iloc[0]['deajeon_index']
    deajeon_df['정규화_인덱스'] = (deajeon_df['deajeon_index'] / deajeon_base) * 100

    kosdaq_base = kosdaq_df.iloc[0]['종가']
    kosdaq_df['정규화_인덱스'] = (kosdaq_df['종가'] / kosdaq_base) * 100

    plt.figure(figsize=(15, 8))
    plt.plot(deajeon_df['날짜'], deajeon_df['정규화_인덱스'], label='대전 인덱스 (정규화)', color='royalblue', linewidth=2)
    plt.plot(kosdaq_df['날짜'], kosdaq_df['정규화_인덱스'], label='코스닥 지수 (정규화)', color='crimson', linewidth=2, alpha=0.8)

    plt.xlabel('날짜', fontsize=12)
    plt.ylabel(f"지수 (기준일: {start_date.strftime('%Y-%m-%d')} = 100)", fontsize=12)
    plt.title('대전 인덱스 vs 코스닥 지수 성과 비교 (정규화)', fontsize=18)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(start_date, end_date)
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✅ [그래프 1] 정규화 비교 그래프가 '{output_path}'에 저장되었습니다.")
    plt.close()

def visualize_dual_axis_aligned(deajeon_df, kosdaq_df, start_date, end_date, output_path):
    """
    그래프 2: 이중 축의 시작점을 시각적으로 정렬하여 각 지수의 변화 추이를 비교합니다.
    """
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    ax1.plot(deajeon_df['날짜'], deajeon_df['deajeon_index'], label='대전 인덱스', color='royalblue')
    ax1.set_xlabel('날짜', fontsize=12)
    ax1.set_ylabel('대전 인덱스', color='royalblue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='royalblue')
    
    ax2 = ax1.twinx()
    ax2.plot(kosdaq_df['날짜'], kosdaq_df['종가'], label='코스닥 지수', color='crimson', alpha=0.8)
    ax2.set_ylabel('코스닥 지수', color='crimson', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='crimson')

    deajeon_initial = deajeon_df.iloc[0]['deajeon_index']
    deajeon_max_dev = max(abs(deajeon_df['deajeon_index'] - deajeon_initial)) * 1.1
    ax1.set_ylim(deajeon_initial - deajeon_max_dev, deajeon_initial + deajeon_max_dev)

    kosdaq_initial = kosdaq_df.iloc[0]['종가']
    kosdaq_max_dev = max(abs(kosdaq_df['종가'] - kosdaq_initial)) * 1.1
    ax2.set_ylim(kosdaq_initial - kosdaq_max_dev, kosdaq_initial + kosdaq_max_dev)

    plt.title('대전 인덱스 vs 코스닥 지수 추이 (이중 축, 시작점 정렬)', fontsize=18)
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=2, fontsize=11)
    plt.xlim(start_date, end_date)
    fig.autofmt_xdate()
    
    plt.tight_layout(rect=[0, 0, 1, 0.9])
    plt.savefig(output_path, dpi=300)
    print(f"✅ [그래프 2] 이중 축(시작점 정렬) 비교 그래프가 '{output_path}'에 저장되었습니다.")
    plt.close()

def visualize_raw_single_axis(deajeon_df, kosdaq_df, start_date, end_date, output_path):
    """
    그래프 3: 정규화 없이 단일 축에 두 지수를 그려 절대적인 규모 차이를 보여줍니다.
    """
    plt.figure(figsize=(15, 8))
    
    plt.plot(deajeon_df['날짜'], deajeon_df['deajeon_index'], label='대전 인덱스', color='royalblue', linewidth=2)
    plt.plot(kosdaq_df['날짜'], kosdaq_df['종가'], label='코스닥 지수', color='crimson', linewidth=2, alpha=0.8)

    plt.xlabel('날짜', fontsize=12)
    plt.ylabel("지수 (원본 값)", fontsize=12)
    plt.title('대전 인덱스 vs 코스닥 지수 규모 비교 (단일 축)', fontsize=18)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(start_date, end_date)
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✅ [그래프 3] 단일 축(원본 값) 비교 그래프가 '{output_path}'에 저장되었습니다.")
    plt.close()

def visualize_market_cap(deajeon_df, kosdaq_df, start_date, end_date, output_path):
    """
    그래프 4: 두 주체의 시가총액을 '억 원' 단위로 비교하는 그래프를 생성합니다. (신규 추가)
    """
    # --- 데이터 단위 변환 (원 -> 억 원) ---
    deajeon_df['시가총액_억원'] = deajeon_df['시가총액'] / 100000000
    kosdaq_df['상장시가총액_억원'] = kosdaq_df['상장시가총액'] / 100000000
    
    # --- 시각화 ---
    plt.figure(figsize=(15, 8))
    
    plt.plot(deajeon_df['날짜'], deajeon_df['시가총액_억원'], label='대전 인덱스 시가총액', color='royalblue', linewidth=2)
    plt.plot(kosdaq_df['날짜'], kosdaq_df['상장시가총액_억원'], label='코스닥 전체 시가총액', color='green', linewidth=2, alpha=0.8)

    plt.xlabel('날짜', fontsize=12)
    plt.ylabel("시가총액 (억 원)", fontsize=12)
    plt.title('대전 인덱스 vs 코스닥 전체 시가총액 비교', fontsize=18)
    plt.legend(loc='best', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xlim(start_date, end_date)
    
    # Y축 라벨에 쉼표(,) 추가 (e.g., 4,000,000)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    plt.gcf().autofmt_xdate()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✅ [그래프 4] 시가총액 비교 그래프가 '{output_path}'에 저장되었습니다.")
    plt.close()


if __name__ == '__main__':
    # --- 한글 폰트 설정 ---
    try:
        font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        plt.rc('font', family=font_name)
    except FileNotFoundError:
        try:
            plt.rc('font', family='AppleGothic')
        except:
            print("경고: 한글 폰트를 찾을 수 없습니다.")
    plt.rcParams['axes.unicode_minus'] = False

    # --- 데이터 경로 설정 ---
    kosdaq_filepath = r'data\kosdaq\data_3607_20250620.csv'
    deajeon_index_filepath = r'data\deajeon_index\deajeon_index_20250620.csv'

    # --- 데이터 로드 ---
    df_kosdaq = read_korean_csv(kosdaq_filepath)
    df_deajeon_index = read_korean_csv(deajeon_index_filepath)

    if df_kosdaq is not None and df_deajeon_index is not None:
        # --- 데이터 전처리 ---
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)

        deajeon_df_processed = df_deajeon_index.copy()
        deajeon_df_processed['날짜'] = pd.to_datetime(deajeon_df_processed['날짜'])
        deajeon_df_processed = deajeon_df_processed[(deajeon_df_processed['날짜'] >= start_date) & (deajeon_df_processed['날짜'] <= end_date)].sort_values('날짜').dropna(subset=['deajeon_index', '시가총액'])
        
        if '일자' in df_kosdaq.columns:
             df_kosdaq.rename(columns={'일자': '날짜'}, inplace=True)

        kosdaq_df_processed = df_kosdaq.copy()
        kosdaq_df_processed['날짜'] = pd.to_datetime(kosdaq_df_processed['날짜'])
        kosdaq_df_processed = kosdaq_df_processed[(kosdaq_df_processed['날짜'] >= start_date) & (kosdaq_df_processed['날짜'] <= end_date)].sort_values('날짜').dropna(subset=['종가', '상장시가총액'])
        
        if deajeon_df_processed.empty or kosdaq_df_processed.empty:
            print("❌ 지정된 기간 내에 데이터가 부족하여 그래프를 생성할 수 없습니다.")
        else:
            # --- 시각화 함수 호출 ---
            today_str = datetime.now().strftime("%Y%m%d")
            
            # 그래프 1
            output_normalized = f'./comparison_normalized_{today_str}.png'
            visualize_normalized(deajeon_df_processed.copy(), kosdaq_df_processed.copy(), start_date, end_date, output_normalized)

            # 그래프 2
            output_dual_axis = f'./comparison_dual_axis_aligned_{today_str}.png'
            visualize_dual_axis_aligned(deajeon_df_processed.copy(), kosdaq_df_processed.copy(), start_date, end_date, output_dual_axis)

            # 그래프 3
            output_raw_single_axis = f'./comparison_raw_single_axis_{today_str}.png'
            visualize_raw_single_axis(deajeon_df_processed.copy(), kosdaq_df_processed.copy(), start_date, end_date, output_raw_single_axis)
            
            # 그래프 4
            output_market_cap = f'./comparison_market_cap_{today_str}.png'
            visualize_market_cap(deajeon_df_processed.copy(), kosdaq_df_processed.copy(), start_date, end_date, output_market_cap)