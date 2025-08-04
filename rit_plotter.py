# rit_plotter.py

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_single_spectrum(df, title="RIT-MS Spectrum", save_path=None):
    """
    단일 스펙트럼 플롯
    
    Args:
        df (pd.DataFrame): 스펙트럼 데이터
        title (str): 그래프 제목
        save_path (str or None): 저장 경로 (None이면 화면에 표시)
    """
    plt.figure(figsize=(10, 6))
    
    # 기본 컬럼명 확인
    x_col = 'RF_ADC_1 [mV]'
    y_col = 'Signal [mV]'
    
    if x_col in df.columns and y_col in df.columns:
        plt.plot(df[x_col], df[y_col], linewidth=1.5, color='blue')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
    else:
        # 컬럼명이 다른 경우 첫 번째와 두 번째 컬럼 사용
        cols = df.columns.tolist()
        if len(cols) >= 2:
            plt.plot(df.iloc[:, 0], df.iloc[:, 1], linewidth=1.5, color='blue')
            plt.xlabel(cols[0])
            plt.ylabel(cols[1])
        else:
            raise ValueError("데이터에 최소 2개의 컬럼이 필요합니다.")
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    else:
        plt.show()

def plot_overlay_spectrum(dfs, labels, title="Overlay RIT-MS Spectrum", save_path=None):
    """
    여러 스펙트럼을 겹쳐서 플롯
    
    Args:
        dfs (list): DataFrame 리스트
        labels (list): 각 스펙트럼의 라벨
        title (str): 그래프 제목
        save_path (str or None): 저장 경로 (None이면 화면에 표시)
    """
    plt.figure(figsize=(12, 8))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    x_col = 'RF_ADC_1 [mV]'
    y_col = 'Signal [mV]'
    
    for i, (df, label) in enumerate(zip(dfs, labels)):
        color = colors[i % len(colors)]
        
        if x_col in df.columns and y_col in df.columns:
            plt.plot(df[x_col], df[y_col], linewidth=1.5, color=color, label=label, alpha=0.8)
        else:
            # 컬럼명이 다른 경우 첫 번째와 두 번째 컬럼 사용
            cols = df.columns.tolist()
            if len(cols) >= 2:
                plt.plot(df.iloc[:, 0], df.iloc[:, 1], linewidth=1.5, color=color, label=label, alpha=0.8)
    
    plt.xlabel(x_col if x_col in dfs[0].columns else dfs[0].columns[0])
    plt.ylabel(y_col if y_col in dfs[0].columns else dfs[0].columns[1])
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Overlay plot saved to {save_path}")
    else:
        plt.show()

def plot_spectrum_with_peaks(df, peaks_df=None, title="RIT-MS Spectrum with Peaks", save_path=None):
    """
    피크가 표시된 스펙트럼 플롯
    
    Args:
        df (pd.DataFrame): 스펙트럼 데이터
        peaks_df (pd.DataFrame or None): 피크 데이터 (x, y 좌표)
        title (str): 그래프 제목
        save_path (str or None): 저장 경로
    """
    plt.figure(figsize=(12, 8))
    
    x_col = 'RF_ADC_1 [mV]'
    y_col = 'Signal [mV]'
    
    # 기본 스펙트럼 플롯
    if x_col in df.columns and y_col in df.columns:
        plt.plot(df[x_col], df[y_col], linewidth=1.5, color='blue', label='Spectrum')
        
        # 피크 표시
        if peaks_df is not None and not peaks_df.empty:
            plt.scatter(peaks_df[x_col], peaks_df[y_col], 
                       color='red', s=50, marker='o', label='Peaks', zorder=5)
            
            # 피크에 텍스트 라벨 추가
            for idx, row in peaks_df.iterrows():
                plt.annotate(f'({row[x_col]:.1f}, {row[y_col]:.1f})', 
                           (row[x_col], row[y_col]), 
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.8)
    
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot with peaks saved to {save_path}")
    else:
        plt.show()

def create_summary_plot(dfs, labels, title="RIT-MS Summary", save_path=None):
    """
    여러 스펙트럼의 요약 플롯 (서브플롯)
    
    Args:
        dfs (list): DataFrame 리스트
        labels (list): 각 스펙트럼의 라벨
        title (str): 전체 그래프 제목
        save_path (str or None): 저장 경로
    """
    n_plots = len(dfs)
    n_cols = 2
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
    if n_plots == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    x_col = 'RF_ADC_1 [mV]'
    y_col = 'Signal [mV]'
    
    for i, (df, label) in enumerate(zip(dfs, labels)):
        ax = axes[i]
        
        if x_col in df.columns and y_col in df.columns:
            ax.plot(df[x_col], df[y_col], linewidth=1.2, color='blue')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        else:
            cols = df.columns.tolist()
            if len(cols) >= 2:
                ax.plot(df.iloc[:, 0], df.iloc[:, 1], linewidth=1.2, color='blue')
                ax.set_xlabel(cols[0])
                ax.set_ylabel(cols[1])
        
        ax.set_title(label, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    # 빈 서브플롯 숨기기
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Summary plot saved to {save_path}")
    else:
        plt.show()
