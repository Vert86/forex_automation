# Windows Installation Guide

If you're on Windows and getting TA-Lib errors, follow these steps:

## Quick Installation (Recommended)

Use the Windows-specific requirements file that excludes TA-Lib:

```bash
pip install -r requirements-windows.txt
```

That's it! The bot will work perfectly without TA-Lib.

## What About TA-Lib?

**You don't need it!** The bot uses pure Python implementations for all technical indicators:
- ATR (Average True Range)
- Moving Averages
- RSI, MACD
- Support/Resistance detection
- Fibonacci levels

All of these work without TA-Lib.

## If You Really Want TA-Lib (Optional)

If you still want to install TA-Lib on Windows:

### Option 1: Install Pre-compiled Wheel (Easiest)

1. Download the appropriate `.whl` file for your Python version from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

2. For Python 3.10 on 64-bit Windows, download:
   `TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`

3. Install it:
   ```bash
   pip install path\to\TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl
   ```

### Option 2: Install Visual C++ Build Tools (Complex)

1. Download Microsoft C++ Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Install with "Desktop development with C++" workload

3. Download and install TA-Lib C library:
   - Download: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-msvc.zip
   - Extract to `C:\ta-lib`

4. Then install via pip:
   ```bash
   pip install ta-lib
   ```

## Verify Installation

Test the bot works:

```bash
python main.py --test
```

You should see the bot scanning symbols and calculating indicators.

## Troubleshooting

**Error: "Cannot import name 'TechnicalIndicators'"**
- This means Python can't find the modules. Make sure you're in the correct directory.

**Error: "No module named 'scipy'"**
- Run: `pip install scipy==1.11.4`

**Error: "API key invalid"**
- Check that `config.py` has the correct API keys (they're pre-configured)

**No signals generated?**
- This is normal! The bot requires confluence (2+ indicators agreeing)
- Good trading setups don't happen every hour

## Next Steps

1. Configure your Telegram bot token in `config.py`
2. Set your account balance in `config.py`
3. Run: `python main.py --symbol EURUSD` to test
4. Run: `python main.py` to start continuous monitoring

See **QUICKSTART.md** for complete setup instructions.
