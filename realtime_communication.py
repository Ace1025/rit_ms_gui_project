# realtime_communication.py

import socket
import threading
import time
import json
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit

class RealtimeDataReceiver(QObject):
    """실시간 데이터 수신기"""
    data_received = pyqtSignal(dict)
    connection_status_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, host='localhost', port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        self.is_running = False
        self.receive_thread = None
        
    def connect_to_server(self):
        """서버에 연결"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            self.connection_status_changed.emit(True)
            
            # 수신 스레드 시작
            self.is_running = True
            self.receive_thread = threading.Thread(target=self._receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
        except Exception as e:
            self.error_occurred.emit(f"연결 실패: {str(e)}")
            self.is_connected = False
            self.connection_status_changed.emit(False)
    
    def disconnect_from_server(self):
        """서버 연결 해제"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        self.is_connected = False
        self.connection_status_changed.emit(False)
    
    def _receive_data(self):
        """데이터 수신 스레드"""
        while self.is_running and self.is_connected:
            try:
                # 데이터 수신 (간단한 JSON 형식)
                data = self.socket.recv(1024).decode('utf-8')
                if data:
                    try:
                        parsed_data = json.loads(data)
                        self.data_received.emit(parsed_data)
                    except json.JSONDecodeError:
                        # 간단한 CSV 형식 데이터 처리
                        self._process_csv_data(data)
                        
            except Exception as e:
                self.error_occurred.emit(f"데이터 수신 오류: {str(e)}")
                break
        
        self.is_connected = False
        self.connection_status_changed.emit(False)
    
    def _process_csv_data(self, csv_data):
        """CSV 형식 데이터 처리"""
        try:
            lines = csv_data.strip().split('\n')
            if len(lines) >= 2:  # 헤더 + 데이터
                headers = lines[0].split(',')
                data_line = lines[1].split(',')
                
                if len(headers) >= 2 and len(data_line) >= 2:
                    data_dict = {
                        'RF_ADC_1 [mV]': float(data_line[0]),
                        'Signal [mV]': float(data_line[1]),
                        'timestamp': time.time()
                    }
                    self.data_received.emit(data_dict)
        except Exception as e:
            self.error_occurred.emit(f"CSV 데이터 처리 오류: {str(e)}")

class MockDataGenerator:
    """테스트용 모의 데이터 생성기"""
    def __init__(self):
        self.base_frequency = 1000  # Hz
        self.amplitude = 100  # mV
        self.noise_level = 5  # mV
        self.time_step = 0.001  # 1ms
        
    def generate_sample_data(self, duration=1.0):
        """샘플 데이터 생성"""
        time_points = np.arange(0, duration, self.time_step)
        rf_data = np.linspace(0, 2000, len(time_points))  # RF ADC 값
        
        # 실제 RIT-MS 신호 시뮬레이션
        signal_data = self.amplitude * np.sin(2 * np.pi * self.base_frequency * time_points)
        signal_data += self.noise_level * np.random.randn(len(time_points))
        
        return {
            'RF_ADC_1 [mV]': rf_data.tolist(),
            'Signal [mV]': signal_data.tolist(),
            'timestamp': time.time()
        }

class RealtimeMonitorWidget(QWidget):
    """실시간 모니터링 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # 실시간 데이터 수신기
        self.data_receiver = RealtimeDataReceiver()
        self.data_receiver.data_received.connect(self.on_data_received)
        self.data_receiver.connection_status_changed.connect(self.on_connection_status_changed)
        self.data_receiver.error_occurred.connect(self.on_error_occurred)
        
        # 모의 데이터 생성기
        self.mock_generator = MockDataGenerator()
        
        # 데이터 저장소
        self.realtime_data = []
        self.max_data_points = 1000
        
        # 업데이트 타이머
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 100ms마다 업데이트
    
    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout()
        
        # 연결 상태 표시
        status_layout = QHBoxLayout()
        
        self.connection_label = QLabel("연결 상태: 연결 안됨")
        self.connection_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
        status_layout.addWidget(self.connection_label)
        
        self.connect_btn = QPushButton("연결")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45B7D1;
            }
        """)
        self.connect_btn.clicked.connect(self.toggle_connection)
        status_layout.addWidget(self.connect_btn)
        
        layout.addLayout(status_layout)
        
        # 실시간 데이터 표시
        self.data_display = QTextEdit()
        self.data_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        self.data_display.setMaximumHeight(150)
        layout.addWidget(self.data_display)
        
        # 통계 정보
        stats_layout = QHBoxLayout()
        
        self.signal_max_label = QLabel("최대 신호: -- mV")
        self.signal_max_label.setStyleSheet("color: #4ECDC4;")
        stats_layout.addWidget(self.signal_max_label)
        
        self.signal_min_label = QLabel("최소 신호: -- mV")
        self.signal_min_label.setStyleSheet("color: #FF6B6B;")
        stats_layout.addWidget(self.signal_min_label)
        
        self.data_count_label = QLabel("데이터 포인트: 0")
        self.data_count_label.setStyleSheet("color: #FFD93D;")
        stats_layout.addWidget(self.data_count_label)
        
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)
    
    def toggle_connection(self):
        """연결 토글"""
        if not self.data_receiver.is_connected:
            self.data_receiver.connect_to_server()
            self.connect_btn.setText("연결 해제")
        else:
            self.data_receiver.disconnect_from_server()
            self.connect_btn.setText("연결")
    
    def on_data_received(self, data):
        """데이터 수신 처리"""
        self.realtime_data.append(data)
        
        # 최대 데이터 포인트 제한
        if len(self.realtime_data) > self.max_data_points:
            self.realtime_data.pop(0)
    
    def on_connection_status_changed(self, connected):
        """연결 상태 변경 처리"""
        if connected:
            self.connection_label.setText("연결 상태: 연결됨")
            self.connection_label.setStyleSheet("color: #4ECDC4; font-weight: bold;")
        else:
            self.connection_label.setText("연결 상태: 연결 안됨")
            self.connection_label.setStyleSheet("color: #FF6B6B; font-weight: bold;")
    
    def on_error_occurred(self, error_msg):
        """오류 처리"""
        self.data_display.append(f"[오류] {error_msg}")
    
    def update_display(self):
        """디스플레이 업데이트"""
        if self.realtime_data:
            latest_data = self.realtime_data[-1]
            
            # 최신 데이터 표시
            display_text = f"RF ADC: {latest_data.get('RF_ADC_1 [mV]', 'N/A'):.2f} mV\n"
            display_text += f"Signal: {latest_data.get('Signal [mV]', 'N/A'):.2f} mV\n"
            display_text += f"Timestamp: {latest_data.get('timestamp', 'N/A')}"
            
            self.data_display.setText(display_text)
            
            # 통계 업데이트
            signals = [data.get('Signal [mV]', 0) for data in self.realtime_data if 'Signal [mV]' in data]
            if signals:
                self.signal_max_label.setText(f"최대 신호: {max(signals):.2f} mV")
                self.signal_min_label.setText(f"최소 신호: {min(signals):.2f} mV")
            
            self.data_count_label.setText(f"데이터 포인트: {len(self.realtime_data)}")
    
    def get_latest_data(self):
        """최신 데이터 반환"""
        if self.realtime_data:
            return self.realtime_data[-1]
        return None
    
    def get_all_data(self):
        """모든 데이터 반환"""
        return self.realtime_data.copy()

class DataAnalysisWidget(QWidget):
    """데이터 분석 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout()
        
        # 분석 옵션
        options_layout = QHBoxLayout()
        
        self.peak_detection_btn = QPushButton("피크 검출")
        self.peak_detection_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        options_layout.addWidget(self.peak_detection_btn)
        
        self.noise_analysis_btn = QPushButton("노이즈 분석")
        self.noise_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #E55A2B;
            }
        """)
        options_layout.addWidget(self.noise_analysis_btn)
        
        self.signal_quality_btn = QPushButton("신호 품질")
        self.signal_quality_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                border: none;
                border-radius: 4px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45B7D1;
            }
        """)
        options_layout.addWidget(self.signal_quality_btn)
        
        layout.addLayout(options_layout)
        
        # 분석 결과 표시
        self.analysis_display = QTextEdit()
        self.analysis_display.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #CCCCCC;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.analysis_display)
        
        self.setLayout(layout)
    
    def analyze_data(self, data):
        """데이터 분석"""
        if not data:
            self.analysis_display.setText("분석할 데이터가 없습니다.")
            return
        
        # 기본 통계 분석
        signals = [point.get('Signal [mV]', 0) for point in data if 'Signal [mV]' in point]
        rf_values = [point.get('RF_ADC_1 [mV]', 0) for point in data if 'RF_ADC_1 [mV]' in point]
        
        if not signals:
            self.analysis_display.setText("유효한 신호 데이터가 없습니다.")
            return
        
        analysis_result = "=== RIT-MS 데이터 분석 결과 ===\n\n"
        
        # 기본 통계
        analysis_result += f"데이터 포인트 수: {len(signals)}\n"
        analysis_result += f"신호 범위: {min(signals):.2f} ~ {max(signals):.2f} mV\n"
        analysis_result += f"평균 신호: {np.mean(signals):.2f} mV\n"
        analysis_result += f"신호 표준편차: {np.std(signals):.2f} mV\n"
        analysis_result += f"RF 범위: {min(rf_values):.2f} ~ {max(rf_values):.2f} mV\n\n"
        
        # 피크 검출
        peaks = self.detect_peaks(signals)
        analysis_result += f"검출된 피크 수: {len(peaks)}\n"
        if peaks:
            peak_values = [signals[i] for i in peaks]
            analysis_result += f"최대 피크: {max(peak_values):.2f} mV\n"
            analysis_result += f"평균 피크 높이: {np.mean(peak_values):.2f} mV\n\n"
        
        # 노이즈 분석
        noise_level = self.analyze_noise(signals)
        analysis_result += f"추정 노이즈 레벨: {noise_level:.2f} mV\n"
        
        # 신호 품질 평가
        quality_score = self.evaluate_signal_quality(signals, noise_level)
        analysis_result += f"신호 품질 점수: {quality_score:.1f}/10\n"
        
        self.analysis_display.setText(analysis_result)
    
    def detect_peaks(self, signals, threshold=0.1):
        """피크 검출"""
        peaks = []
        for i in range(1, len(signals) - 1):
            if (signals[i] > signals[i-1] and 
                signals[i] > signals[i+1] and 
                signals[i] > np.mean(signals) + threshold * np.std(signals)):
                peaks.append(i)
        return peaks
    
    def analyze_noise(self, signals):
        """노이즈 분석"""
        # 간단한 노이즈 레벨 추정
        return np.std(signals)
    
    def evaluate_signal_quality(self, signals, noise_level):
        """신호 품질 평가"""
        signal_range = max(signals) - min(signals)
        snr = signal_range / noise_level if noise_level > 0 else 0
        quality = min(10, snr / 2)  # 0-10 스케일
        return quality