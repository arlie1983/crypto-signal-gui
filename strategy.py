import pandas as pd, numpy as np

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def macd_series(close, fast=12, slow=26, signal=9):
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    macd = fast_ema - slow_ema
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=period, min_periods=1).mean()
    ma_down = down.rolling(window=period, min_periods=1).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))

def true_range(df):
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - df['close'].shift()).abs()
    tr3 = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr

def atr(df, period=14):
    tr = true_range(df)
    return tr.rolling(window=period, min_periods=1).mean()

def generate_signal_from_ohlcv(df, symbol='BTC/USDT', timeframe='1h'):
    # uses 1 timeframe only here; for full multi-timeframe pass aggregated 4h as well
    df = df.copy().reset_index(drop=True)
    df['ema_short'] = ema(df['close'], 8)
    df['ema_long'] = ema(df['close'], 21)
    _, _, macd_hist = macd_series(df['close'])
    df['macd_hist'] = macd_hist
    df['rsi'] = rsi(df['close'], 14)
    df['atr'] = atr(df, 14)
    cur = df.iloc[-1]
    prev = df.iloc[-2]
    votes = 0
    crossed_up = (prev['ema_short'] <= prev['ema_long']) and (cur['ema_short'] > cur['ema_long'])
    if crossed_up: votes += 1
    macd_rising = (cur['macd_hist'] > 0) and (cur['macd_hist'] > prev['macd_hist'])
    if macd_rising: votes += 1
    vol_spike = False
    try:
        vol_avg = df['volume'].rolling(20).mean().iloc[-1]
        vol_spike = cur['volume'] > vol_avg * 1.5
    except Exception:
        vol_spike = False
    if vol_spike and (40 < cur['rsi'] < 70): votes += 1
    if votes >= 2:
        entry = float(cur['close'])
        atr_v = float(cur['atr']) if not np.isnan(cur['atr']) else 0.0
        stop = max(entry - atr_v * 2.5, entry * 0.995)
        tp1 = entry + atr_v * 2
        tp2 = entry + atr_v * 4
        return {'signal':'BUY','entry':round(entry,2),'stop':round(stop,2),'tp1':round(tp1,2),'tp2':round(tp2,2),'atr':round(atr_v,6)}
    # check sell (reverse)
    crossed_down = (prev['ema_short'] >= prev['ema_long']) and (cur['ema_short'] < cur['ema_long'])
    macd_falling = (cur['macd_hist'] < 0) and (cur['macd_hist'] < prev['macd_hist'])
    if crossed_down and macd_falling:
        entry = float(cur['close'])
        atr_v = float(cur['atr']) if not np.isnan(cur['atr']) else 0.0
        stop = min(entry + atr_v*2.5, entry*1.005)
        tp1 = entry - atr_v*2
        tp2 = entry - atr_v*4
        return {'signal':'SELL','entry':round(entry,2),'stop':round(stop,2),'tp1':round(tp1,2),'tp2':round(tp2,2),'atr':round(atr_v,6)}
    return {'signal':'HOLD'}
