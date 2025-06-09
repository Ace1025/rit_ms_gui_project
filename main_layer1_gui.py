# main_layer1_gui.py

import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog, 
                             QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem)
from rit_data_loader import load_rit_csv
from rit_plotter import plot_single_spectrum, plot_overlay_spectrum

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIT-MS Spectrum Viewer")
        self.setGeometry(100, 100, 600, 400)

        self.file_path = ""
        self.df_dict = {}  # 시트별 DataFrame 저장

        # 위젯 생성
        self.browse_btn = QPushButton("Browse CSV / Excel")
        self.sheet_combo = QComboBox()
        self.plot_btn = QPushButton("Plot")
        self.overlay_list = QListWidget()
        self.overlay_btn = QPushButton("Overlay Plot")
        self.save_btn = QPushButton("Save Plot")

        # 레이아웃 구성
        layout = QVBoxLayout()
        layout.addWidget(self.browse_btn)
        layout.addWidget(QLabel("Select Sheet:"))
        layout.addWidget(self.sheet_combo)
        layout.addWidget(self.plot_btn)
        layout.addWidget(QLabel("Overlay Select (multi-select with Ctrl):"))
        layout.addWidget(self.overlay_list)
        layout.addWidget(self.overlay_btn)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

        # 이벤트 연결
        self.browse_btn.clicked.connect(self.browse_file)
        self.plot_btn.clicked.connect(self.plot_spectrum)
        self.overlay_btn.clicked.connect(self.plot_overlay)
        self.save_btn.clicked.connect(self.save_plot)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV or Excel", "", 
                                                   "Excel Files (*.xlsx);;CSV Files (*.csv)")
        if file_name:
            self.file_path = file_name
            self.df_dict.clear()
            self.sheet_combo.clear()
            self.overlay_list.clear()

            if file_name.endswith('.xlsx'):
                xls = pd.ExcelFile(file_name)
                for sheet in xls.sheet_names:
                    df = load_rit_csv(file_name, sheet)
                    self.df_dict[sheet] = df
                    self.sheet_combo.addItem(sheet)
                    self.overlay_list.addItem(sheet)
            else:
                df = load_rit_csv(file_name, None)
                self.df_dict["CSV"] = df
                self.sheet_combo.addItem("CSV")
                self.overlay_list.addItem("CSV")

            QMessageBox.information(self, "File Loaded", f"Loaded: {os.path.basename(file_name)}")

    def plot_spectrum(self):
        sheet = self.sheet_combo.currentText()
        if sheet and sheet in self.df_dict:
            df = self.df_dict[sheet]
            plot_single_spectrum(df, title=f"{sheet} - RIT-MS Spectrum")
        else:
            QMessageBox.warning(self, "Warning", "No sheet selected or data not loaded.")

    def plot_overlay(self):
        selected_items = self.overlay_list.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(self, "Warning", "Select at least 2 sheets for overlay.")
            return

        dfs = []
        labels = []
        for item in selected_items:
            sheet = item.text()
            if sheet in self.df_dict:
                dfs.append(self.df_dict[sheet])
                labels.append(sheet)

        plot_overlay_spectrum(dfs, labels, title="Overlay RIT-MS Spectrum")

    def save_plot(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png)")
        if save_path:
            # 저장용으로는 단일 시트 plot
            sheet = self.sheet_combo.currentText()
            if sheet and sheet in self.df_dict:
                df = self.df_dict[sheet]
                plot_single_spectrum(df, title=f"{sheet} - RIT-MS Spectrum", save_path=save_path)
                QMessageBox.information(self, "Saved", f"Plot saved to {save_path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
