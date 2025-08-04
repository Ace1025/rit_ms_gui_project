# rit_plotter.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

def plot_single_spectrum(df, title="RIT-MS Spectrum", save_path=None):
    """
    단일 스펙트럼을 플롯
    
    Args:
        df (pd.DataFrame): RIT-MS 데이터
        title (str): 플롯 제목
        save_path (str, optional): 저장 경로
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # RF_ADC_1 [mV]를 x축으로, Signal [mV]를 y축으로
    x_data = df['RF_ADC_1 [mV]']
    y_data = df['Signal [mV]']
    
    ax.plot(x_data, y_data, linewidth=1.5, color='#007ACC')
    ax.set_xlabel('RF ADC 1 [mV]', fontsize=12)
    ax.set_ylabel('Signal [mV]', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 스타일링
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
    
    plt.close()

def plot_overlay_spectrum(dfs, labels, title="Overlay RIT-MS Spectrum", save_path=None):
    """
    여러 스펙트럼을 오버레이로 플롯
    
    Args:
        dfs (list): DataFrame 리스트
        labels (list): 각 스펙트럼의 라벨
        title (str): 플롯 제목
        save_path (str, optional): 저장 경로
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#007ACC', '#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, (df, label) in enumerate(zip(dfs, labels)):
        x_data = df['RF_ADC_1 [mV]']
        y_data = df['Signal [mV]']
        color = colors[i % len(colors)]
        
        ax.plot(x_data, y_data, linewidth=1.5, label=label, color=color)
    
    ax.set_xlabel('RF ADC 1 [mV]', fontsize=12)
    ax.set_ylabel('Signal [mV]', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 스타일링
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()
    
    plt.close()

class RITPlotterWidget:
    """
    PyQt 위젯으로 사용할 수 있는 RIT-MS 플로터
    """
    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
    def plot_spectrum(self, df, title="RIT-MS Spectrum"):
        """위젯에 스펙트럼 플롯"""
        self.ax.clear()
        
        x_data = df['RF_ADC_1 [mV]']
        y_data = df['Signal [mV]']
        
        self.ax.plot(x_data, y_data, linewidth=1.5, color='#007ACC')
        self.ax.set_xlabel('RF ADC 1 [mV]', fontsize=12)
        self.ax.set_ylabel('Signal [mV]', fontsize=12)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # 스타일링
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_overlay(self, dfs, labels, title="Overlay RIT-MS Spectrum"):
        """위젯에 오버레이 스펙트럼 플롯"""
        self.ax.clear()
        
        colors = ['#007ACC', '#FF6B35', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, (df, label) in enumerate(zip(dfs, labels)):
            x_data = df['RF_ADC_1 [mV]']
            y_data = df['Signal [mV]']
            color = colors[i % len(colors)]
            
            self.ax.plot(x_data, y_data, linewidth=1.5, label=label, color=color)
        
        self.ax.set_xlabel('RF ADC 1 [mV]', fontsize=12)
        self.ax.set_ylabel('Signal [mV]', fontsize=12)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # 스타일링
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def clear(self):
        """플롯 클리어"""
        self.ax.clear()
        self.canvas.draw()
    
    def save_plot(self, save_path):
        """플롯 저장"""
        self.figure.savefig(save_path, dpi=300, bbox_inches='tight')
