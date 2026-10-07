# QR Code Printer

A desktop QR code label tool built with Python and PySide6. It can generate QR previews, set label dimensions and quantity, and load QR data from a CSV file.

> **Printing note:** The current app uses a mock printer. The Print action writes the job details to the terminal; it does not send a job to a physical printer yet.

## Requirements

- Python 3.10 or newer
- Git, if you are cloning the project

## macOS

Open Terminal, navigate to the project folder, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Windows

Open PowerShell, navigate to the project folder, and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

If PowerShell blocks virtual-environment activation, use Command Prompt instead and activate with:

```bat
.venv\Scripts\activate.bat
```

Then run the two `python -m pip install ...` commands and `python main.py` in that same Command Prompt window.

## Install dependencies again

After activating the virtual environment, install or update the project dependencies with:

```bash
python -m pip install -r requirements.txt
```

The dependency list is maintained in [`requirements.txt`](requirements.txt).
