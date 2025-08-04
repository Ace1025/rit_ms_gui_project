# create_sample_data.py - 테스트용 샘플 데이터 생성

import pandas as pd
import numpy as np

def create_sample_rit_data():
    """RIT-MS 샘플 데이터 생성"""
    
    # RF ADC 값 (0-2000 mV 범위)
    rf_adc = np.linspace(0, 2000, 1000)
    
    # 실제 RIT-MS 신호 시뮬레이션
    # 여러 피크가 있는 스펙트럼
    signal = np.zeros_like(rf_adc)
    
    # 피크 1 (주요 피크)
    peak1_center = 500
    peak1_width = 50
    signal += 100 * np.exp(-(rf_adc - peak1_center)**2 / (2 * peak1_width**2))
    
    # 피크 2 (보조 피크)
    peak2_center = 1200
    peak2_width = 30
    signal += 60 * np.exp(-(rf_adc - peak2_center)**2 / (2 * peak2_width**2))
    
    # 피크 3 (작은 피크)
    peak3_center = 1800
    peak3_width = 40
    signal += 40 * np.exp(-(rf_adc - peak3_center)**2 / (2 * peak3_width**2))
    
    # 노이즈 추가
    noise = np.random.normal(0, 2, len(rf_adc))
    signal += noise
    
    # DataFrame 생성
    df = pd.DataFrame({
        'RF_ADC_1 [mV]': rf_adc,
        'Signal [mV]': signal
    })
    
    return df

def create_multiple_samples():
    """여러 샘플 데이터 생성"""
    
    # 기본 데이터
    base_df = create_sample_rit_data()
    
    # 샘플 1 (기본)
    base_df.to_csv('sample_data_1.csv', index=False)
    
    # 샘플 2 (노이즈가 더 많은 버전)
    df2 = base_df.copy()
    df2['Signal [mV]'] += np.random.normal(0, 5, len(df2))
    df2.to_csv('sample_data_2.csv', index=False)
    
    # 샘플 3 (피크 위치가 다른 버전)
    df3 = base_df.copy()
    df3['RF_ADC_1 [mV]'] = df3['RF_ADC_1 [mV]'] * 1.1  # 스케일 조정
    df3.to_csv('sample_data_3.csv', index=False)
    
    # Excel 파일로 여러 시트 생성
    with pd.ExcelWriter('sample_data.xlsx') as writer:
        base_df.to_excel(writer, sheet_name='Sample_1', index=False)
        df2.to_excel(writer, sheet_name='Sample_2', index=False)
        df3.to_excel(writer, sheet_name='Sample_3', index=False)
    
    print("샘플 데이터가 생성되었습니다:")
    print("- sample_data_1.csv")
    print("- sample_data_2.csv") 
    print("- sample_data_3.csv")
    print("- sample_data.xlsx (여러 시트 포함)")

if __name__ == "__main__":
    create_multiple_samples()