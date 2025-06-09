# rit_data_loader.py

import pandas as pd

def load_rit_csv(filepath, sheet_name=None):
    """
    RIT-MS CSV 또는 Excel 파일을 읽어 DataFrame으로 반환

    Args:
        filepath (str): 파일 경로 (.csv 또는 .xlsx)
        sheet_name (str or None): 엑셀의 경우 시트명 (csv는 None)

    Returns:
        pd.DataFrame: 데이터프레임
    """
    if filepath.endswith('.xlsx'):
        if sheet_name is None:
            raise ValueError("Excel 파일은 sheet_name을 지정해야 합니다.")
        df = pd.read_excel(filepath, sheet_name=sheet_name)
    else:
        # csv 파일의 경우는 시트 개념이 없음
        df = pd.read_csv(filepath)

    # 컬럼 이름 확인 후 클린업 가능 (여기서 필요한 경우 수정 가능)
    expected_columns = ['RF_ADC_1 [mV]', 'Signal [mV]']

    for col in expected_columns:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 '{col}' 이(가) 파일에 없습니다!")

    return df

def save_to_pickle(df, path):
    """
    DataFrame을 pickle 파일로 저장

    Args:
        df (pd.DataFrame): 저장할 데이터프레임
        path (str): 저장 경로 (.pkl)
    """
    df.to_pickle(path)

def load_from_pickle(path):
    """
    pickle 파일에서 DataFrame 불러오기

    Args:
        path (str): pickle 파일 경로

    Returns:
        pd.DataFrame: 불러온 데이터프레임
    """
    return pd.read_pickle(path)
