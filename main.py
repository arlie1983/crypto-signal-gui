import sys, threading, time
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout
import ccxt, pandas as pd, numpy as np
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from win10toast import ToastNotifier
from strategy import generate_signal_from_ohlcv

TOASTER = ToastNotifier()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=3, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width,height), dpi=dpi)
        super().__init__(self.fig)
        plt.tight_layout()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Crypto Signal - Windows 11 (Prototype)')
        self.resize(900,600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        top = QHBoxLayout()
        self.symbol_cb = QComboBox(); self.symbol_cb.addItems(['BTC/USDT','ETH/USDT','BNB/USDT'])
        self.tf_cb = QComboBox(); self.tf_cb.addItems(['1h','4h','15m'])
        self.refresh_btn = QPushButton('Refresh')
        top.addWidget(QLabel('Symbol:')); top.addWidget(self.symbol_cb)
        top.addWidget(QLabel('Timeframe:')); top.addWidget(self.tf_cb)
        top.addWidget(self.refresh_btn)
        self.layout.addLayout(top)

        info_layout = QHBoxLayout()
        self.signal_label = QLabel('Signal: -'); self.signal_label.setStyleSheet('font-size:20px; font-weight:bold;')
        self.details_label = QLabel('Entry: -   Stop: -   TP1: -   TP2: -')
        info_layout.addWidget(self.signal_label)
        info_layout.addWidget(self.details_label)
        self.layout.addLayout(info_layout)

        self.canvas = MplCanvas(self, width=8, height=4, dpi=100)
        self.layout.addWidget(self.canvas)

        self.refresh_btn.clicked.connect(self.refresh)

        # background auto refresh
        self._stop = False
        self.thread = threading.Thread(target=self.auto_refresh, daemon=True)
        self.thread.start()

    def closeEvent(self, event):
        self._stop = True
        event.accept()

    def auto_refresh(self):
        while not self._stop:
            try:
                self.refresh()
            except Exception as e:
                print('Auto-refresh error', e)
            time.sleep(60)

    def refresh(self):
        symbol = self.symbol_cb.currentText()
        tf = self.tf_cb.currentText()
        # fetch ohlcv
        ex = ccxt.binance({'enableRateLimit': True})
        limit = 200
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        res = generate_signal_from_ohlcv(df, symbol=symbol, timeframe=tf)
        sig = res.get('signal','HOLD')
        entry = res.get('entry'); stop = res.get('stop'); tp1 = res.get('tp1'); tp2 = res.get('tp2')
        # update UI
        self.signal_label.setText(f'Signal: {sig}')
        if sig=='BUY':
            self.signal_label.setStyleSheet('color:green; font-size:20px; font-weight:bold;')
        elif sig=='SELL':
            self.signal_label.setStyleSheet('color:red; font-size:20px; font-weight:bold;')
        else:
            self.signal_label.setStyleSheet('color:black; font-size:20px; font-weight:bold;')
        self.details_label.setText(f'Entry: {entry}   Stop: {stop}   TP1: {tp1}   TP2: {tp2}')
        # plot candles (simple)
        self.canvas.ax.clear()
        self.canvas.ax.plot(df['timestamp'], df['close'], label='close')
        self.canvas.ax.set_title(f'{symbol} {tf} - Close Price')
        self.canvas.ax.legend()
        self.canvas.draw()
        # notification on signal change
        try:
            if sig in ('BUY','SELL'):
                TOASTER.show_toast(f'{sig} signal - {symbol}', f'Entry: {entry} Stop: {stop}', duration=6, threaded=True)
        except Exception as e:
            print('Notification error', e)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
