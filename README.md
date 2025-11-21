Windows Crypto Signal App - Prototype (PyQt)
===========================================

What this is
- A simple PyQt GUI app that fetches OHLCV from Binance (public), computes signals using EMA+MACD+RSI+ATR ensemble,
  and displays the current signal (BUY/SELL/HOLD), suggested entry, stop, and two take-profits.
- Includes embedded matplotlib candlestick chart.

Requirements (on Windows 11)
- Python 3.10+ (recommended)
- pip install -r requirements.txt
- To build .exe: install PyInstaller (`pip install pyinstaller`) and run `build_exe.bat`

Quick start (run with Python)
1. unzip the project
2. open command prompt in the project folder
3. python -m venv .venv
4. .\.venv\Scripts\activate
5. pip install -r requirements.txt
6. python main.py

Build EXE (optional)
- After installing requirements and PyInstaller, run `build_exe.bat`. It will produce `dist\crypto_signal_gui\crypto_signal_gui.exe`.

Notes & Security
- This app uses public OHLCV data only (no API keys). If you add trading features, **never** embed API secrets in the app.
- Always paper-trade before using real funds.
