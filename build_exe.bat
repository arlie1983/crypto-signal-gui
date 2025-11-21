\
        @echo off
        REM Build debug exe with PyInstaller
        REM Make sure you activated your venv and installed requirements first.
        pyinstaller --noconfirm --onefile --windowed --name crypto_signal_gui main.py
        echo Build finished. Check the dist\crypto_signal_gui.exe
        pause
