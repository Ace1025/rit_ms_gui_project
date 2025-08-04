# main_layer1_gui.py - Modern RIT-MS GUI with Cursor-style design

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget
from rit_data_loader import load_rit_csv
from rit_plotter import RITPlotterWidget
from realtime_communication import RealtimeMonitorWidget, DataAnalysisWidget

class ModernButton(QPushButton):
    """현대적인 스타일의 버튼"""
    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                border: 1px solid #007ACC;
            }
            QPushButton:pressed {
                background-color: #007ACC;
            }
            QPushButton:disabled {
                background-color: #1E1E1E;
                color: #6B6B6B;
            }
        """)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))

class CollapsibleWidget(QWidget):
    """접을 수 있는 위젯"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.is_collapsed = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 헤더 버튼
        self.header_btn = QPushButton(f"▼ {self.title}")
        self.header_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: #2D2D30;
                color: #CCCCCC;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3F3F46;
            }
        """)
        self.header_btn.clicked.connect(self.toggle_collapse)
        layout.addWidget(self.header_btn)
        
        # 콘텐츠 영역
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 5, 15, 10)
        layout.addWidget(self.content_widget)
        
        self.setLayout(layout)
    
    def toggle_collapse(self):
        """접기/펼치기 토글"""
        self.is_collapsed = not self.is_collapsed
        self.content_widget.setVisible(not self.is_collapsed)
        
        if self.is_collapsed:
            self.header_btn.setText(f"▶ {self.title}")
        else:
            self.header_btn.setText(f"▼ {self.title}")
    
    def add_widget(self, widget):
        """위젯 추가"""
        self.content_layout.addWidget(widget)

class SidebarWidget(QWidget):
    """확장/축소 가능한 사이드바"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border-right: 1px solid #3F3F46;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 헤더
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet("background-color: #2D2D30; border-bottom: 1px solid #3F3F46;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("RIT-MS Explorer")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title_label)
        
        layout.addWidget(header)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #252526;
            }
            QScrollBar:vertical {
                background-color: #2D2D30;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3F3F46;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #007ACC;
            }
        """)
        
        # 스크롤 콘텐츠
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        
        # 파일 관리 섹션
        file_section = CollapsibleWidget("📁 파일 관리")
        file_btn1 = QPushButton("📂 파일 열기")
        file_btn1.setProperty("action", "open_file")
        file_btn1.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        file_section.add_widget(file_btn1)
        
        file_btn2 = QPushButton("💾 저장")
        file_btn2.setProperty("action", "save_file")
        file_btn2.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        file_section.add_widget(file_btn2)
        
        scroll_layout.addWidget(file_section)
        
        # 분석 도구 섹션
        analysis_section = CollapsibleWidget("📊 분석 도구")
        analysis_btn1 = QPushButton("📈 단일 스펙트럼")
        analysis_btn1.setProperty("action", "single_spectrum")
        analysis_btn1.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        analysis_section.add_widget(analysis_btn1)
        
        analysis_btn2 = QPushButton("🔄 오버레이 분석")
        analysis_btn2.setProperty("action", "overlay_analysis")
        analysis_btn2.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        analysis_section.add_widget(analysis_btn2)
        
        analysis_btn3 = QPushButton("📊 통계 분석")
        analysis_btn3.setProperty("action", "statistical_analysis")
        analysis_btn3.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        analysis_section.add_widget(analysis_btn3)
        
        scroll_layout.addWidget(analysis_section)
        
        # 실시간 모니터링 섹션
        realtime_section = CollapsibleWidget("⚡ 실시간 모니터링")
        realtime_btn1 = QPushButton("📡 실시간 데이터")
        realtime_btn1.setProperty("action", "realtime_data")
        realtime_btn1.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        realtime_section.add_widget(realtime_btn1)
        
        realtime_btn2 = QPushButton("🔗 연결 상태")
        realtime_btn2.setProperty("action", "connection_status")
        realtime_btn2.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        realtime_section.add_widget(realtime_btn2)
        
        scroll_layout.addWidget(realtime_section)
        
        # 설정 섹션
        settings_section = CollapsibleWidget("⚙️ 설정")
        settings_btn1 = QPushButton("🎨 테마 설정")
        settings_btn1.setProperty("action", "theme_settings")
        settings_btn1.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 15px;
                border: none;
                background-color: transparent;
                color: #CCCCCC;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
                color: #FFFFFF;
            }
        """)
        settings_section.add_widget(settings_btn1)
        
        scroll_layout.addWidget(settings_section)
        
        # 하단 여백
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)

class MainContentWidget(QWidget):
    """메인 콘텐츠 영역"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 상단 툴바
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 메인 콘텐츠 영역 (탭 위젯)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
                color: #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #3F3F46;
            }
        """)
        
        # 플로터 탭
        self.plotter_widget = RITPlotterWidget()
        self.tab_widget.addTab(self.plotter_widget.canvas, "📈 스펙트럼")
        
        # 실시간 모니터링 탭
        self.realtime_widget = RealtimeMonitorWidget()
        self.tab_widget.addTab(self.realtime_widget, "⚡ 실시간")
        
        # 데이터 분석 탭
        self.analysis_widget = DataAnalysisWidget()
        self.tab_widget.addTab(self.analysis_widget, "📊 분석")
        
        # 데이터 테이블 탭
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #CCCCCC;
                gridline-color: #3F3F46;
                border: none;
            }
            QHeaderView::section {
                background-color: #2D2D30;
                color: #CCCCCC;
                padding: 8px;
                border: none;
                border-right: 1px solid #3F3F46;
                border-bottom: 1px solid #3F3F46;
            }
        """)
        self.tab_widget.addTab(self.data_table, "📋 데이터")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def create_toolbar(self):
        """상단 툴바 생성"""
        toolbar = QWidget()
        toolbar.setFixedHeight(40)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #2D2D30;
                border-bottom: 1px solid #3F3F46;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # 파일 정보
        self.file_info_label = QLabel("파일이 선택되지 않음")
        self.file_info_label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        layout.addWidget(self.file_info_label)
        
        layout.addStretch()
        
        # 상태 표시
        self.status_label = QLabel("준비됨")
        self.status_label.setStyleSheet("color: #4ECDC4; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        return toolbar

class ModernRITMSWindow(QMainWindow):
    """현대적인 RIT-MS 메인 윈도우"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIT-MS Analysis Platform v2.0")
        self.setGeometry(100, 100, 1600, 1000)
        
        # 데이터 저장소
        self.file_path = ""
        self.df_dict = {}
        self.current_data = None
        
        # UI 설정
        self.setup_ui()
        self.setup_animations()
        self.setup_connections()
        
    def setup_ui(self):
        """UI 설정"""
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 사이드바
        self.sidebar = SidebarWidget()
        main_layout.addWidget(self.sidebar)
        
        # 메인 콘텐츠
        self.main_content = MainContentWidget()
        main_layout.addWidget(self.main_content)
        
        # 윈도우 스타일
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
        """)
        
        # 메뉴바 설정
        self.setup_menubar()
        
    def setup_menubar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2D2D30;
                color: #CCCCCC;
                border-bottom: 1px solid #3F3F46;
            }
            QMenuBar::item {
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #3F3F46;
            }
        """)
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        file_menu.setStyleSheet("""
            QMenu {
                background-color: #2D2D30;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #007ACC;
            }
        """)
        
        open_action = QAction("파일 열기", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("저장", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # 분석 메뉴
        analysis_menu = menubar.addMenu("분석")
        
        plot_action = QAction("스펙트럼 플롯", self)
        plot_action.triggered.connect(self.plot_spectrum)
        analysis_menu.addAction(plot_action)
        
        overlay_action = QAction("오버레이 분석", self)
        overlay_action.triggered.connect(self.plot_overlay)
        analysis_menu.addAction(overlay_action)
        
        # 실시간 메뉴
        realtime_menu = menubar.addMenu("실시간")
        
        connect_action = QAction("연결", self)
        connect_action.triggered.connect(self.toggle_realtime_connection)
        realtime_menu.addAction(connect_action)
        
    def setup_connections(self):
        """시그널 연결"""
        # 사이드바 버튼들 연결
        for child in self.sidebar.findChildren(QPushButton):
            if child.property("action"):
                child.clicked.connect(lambda checked, action=child.property("action"): self.handle_sidebar_action(action))
    
    def setup_animations(self):
        """애니메이션 설정"""
        # 사이드바 토글 애니메이션
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def handle_sidebar_action(self, action):
        """사이드바 액션 처리"""
        if action == "open_file":
            self.open_file()
        elif action == "save_file":
            self.save_file()
        elif action == "single_spectrum":
            self.plot_spectrum()
        elif action == "overlay_analysis":
            self.plot_overlay()
        elif action == "statistical_analysis":
            self.perform_statistical_analysis()
        elif action == "realtime_data":
            self.main_content.tab_widget.setCurrentIndex(1)  # 실시간 탭
        elif action == "connection_status":
            self.show_connection_status()
    
    def open_file(self):
        """파일 열기"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "RIT-MS 파일 열기", 
            "", 
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_name:
            try:
                self.file_path = file_name
                self.df_dict.clear()
                
                if file_name.endswith('.xlsx'):
                    xls = pd.ExcelFile(file_name)
                    for sheet in xls.sheet_names:
                        df = load_rit_csv(file_name, sheet)
                        self.df_dict[sheet] = df
                else:
                    df = load_rit_csv(file_name, None)
                    self.df_dict["CSV"] = df
                
                # UI 업데이트
                self.main_content.file_info_label.setText(f"파일: {os.path.basename(file_name)}")
                self.main_content.status_label.setText("데이터 로드됨")
                
                # 첫 번째 데이터로 플롯
                if self.df_dict:
                    first_key = list(self.df_dict.keys())[0]
                    self.current_data = self.df_dict[first_key]
                    self.plot_spectrum()
                    
                # 데이터 테이블 업데이트
                self.update_data_table()
                    
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일을 열 수 없습니다: {str(e)}")
    
    def save_file(self):
        """파일 저장"""
        if self.current_data is None:
            QMessageBox.warning(self, "경고", "저장할 데이터가 없습니다.")
            return
            
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "플롯 저장", 
            "", 
            "PNG Files (*.png);;PDF Files (*.pdf)"
        )
        
        if save_path:
            try:
                self.main_content.plotter_widget.save_plot(save_path)
                self.main_content.status_label.setText("저장 완료")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"저장 중 오류가 발생했습니다: {str(e)}")
    
    def plot_spectrum(self):
        """스펙트럼 플롯"""
        if self.current_data is not None:
            self.main_content.plotter_widget.plot_spectrum(
                self.current_data, 
                "RIT-MS Spectrum"
            )
            self.main_content.status_label.setText("플롯 완료")
            self.main_content.tab_widget.setCurrentIndex(0)  # 플로터 탭
        else:
            QMessageBox.warning(self, "경고", "플롯할 데이터가 없습니다.")
    
    def plot_overlay(self):
        """오버레이 플롯"""
        if len(self.df_dict) < 2:
            QMessageBox.warning(self, "경고", "오버레이를 위해 최소 2개의 데이터셋이 필요합니다.")
            return
            
        # 간단한 오버레이 (첫 2개 데이터셋)
        keys = list(self.df_dict.keys())[:2]
        dfs = [self.df_dict[key] for key in keys]
        
        self.main_content.plotter_widget.plot_overlay(
            dfs, 
            keys, 
            "Overlay RIT-MS Spectrum"
        )
        self.main_content.status_label.setText("오버레이 완료")
        self.main_content.tab_widget.setCurrentIndex(0)  # 플로터 탭
    
    def perform_statistical_analysis(self):
        """통계 분석 수행"""
        if self.current_data is not None:
            # 실시간 데이터를 분석 위젯으로 전달
            realtime_data = self.main_content.realtime_widget.get_all_data()
            if realtime_data:
                self.main_content.analysis_widget.analyze_data(realtime_data)
            else:
                # 파일 데이터를 DataFrame으로 변환하여 분석
                data_for_analysis = []
                for i, row in self.current_data.iterrows():
                    data_for_analysis.append({
                        'RF_ADC_1 [mV]': row['RF_ADC_1 [mV]'],
                        'Signal [mV]': row['Signal [mV]'],
                        'timestamp': i
                    })
                self.main_content.analysis_widget.analyze_data(data_for_analysis)
            
            self.main_content.tab_widget.setCurrentIndex(2)  # 분석 탭
        else:
            QMessageBox.warning(self, "경고", "분석할 데이터가 없습니다.")
    
    def toggle_realtime_connection(self):
        """실시간 연결 토글"""
        self.main_content.realtime_widget.toggle_connection()
    
    def show_connection_status(self):
        """연결 상태 표시"""
        is_connected = self.main_content.realtime_widget.data_receiver.is_connected
        status = "연결됨" if is_connected else "연결 안됨"
        QMessageBox.information(self, "연결 상태", f"실시간 데이터 연결: {status}")
    
    def update_data_table(self):
        """데이터 테이블 업데이트"""
        if self.current_data is not None:
            self.main_content.data_table.setRowCount(len(self.current_data))
            self.main_content.data_table.setColumnCount(2)
            self.main_content.data_table.setHorizontalHeaderLabels(['RF ADC 1 [mV]', 'Signal [mV]'])
            
            for i, (_, row) in enumerate(self.current_data.iterrows()):
                self.main_content.data_table.setItem(i, 0, QTableWidgetItem(f"{row['RF_ADC_1 [mV]']:.2f}"))
                self.main_content.data_table.setItem(i, 1, QTableWidgetItem(f"{row['Signal [mV]']:.2f}"))

def main():
    app = QApplication(sys.argv)
    
    # 애플리케이션 스타일 설정
    app.setStyle("Fusion")
    
    # 폰트 설정
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # 윈도우 생성 및 표시
    window = ModernRITMSWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
