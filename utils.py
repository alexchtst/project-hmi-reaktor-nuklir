import os
import sys
from pathlib import Path

def resource_path(relative_path):
    """
    Get absolute path to resource (READ-ONLY), works for dev and for PyInstaller.
    Gunakan ini untuk: asset (gambar, icon), ui files, library, module
    
    Args:
        relative_path: Path relatif dari root project (contoh: "asset/icon.png")
    
    Returns:
        Absolute path untuk resource yang di-bundle dalam executable
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def data_path(relative_path=""):
    """
    Get absolute path to user data directory (READ-WRITE).
    Gunakan ini untuk: menyimpan/membaca CSV, JSON, hasil simulasi, config user
    
    Data akan disimpan di:
    - Windows: C:/Users/[Username]/AppData/Local/ReaktorNuklir/data/
    - Linux: ~/.local/share/ReaktorNuklir/data/
    - Mac: ~/Library/Application Support/ReaktorNuklir/data/
    
    Args:
        relative_path: Path relatif dalam folder data (contoh: "results/sim1.csv")
    
    Returns:
        Absolute path untuk data yang bisa ditulis user
    """
    if sys.platform == "win32":
        base_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ReaktorNuklir', 'data')
    elif sys.platform == "darwin":  # macOS
        base_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'ReaktorNuklir', 'data')
    else:  # Linux
        base_path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'ReaktorNuklir', 'data')
    
    # Buat folder jika belum ada
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Return full path jika relative_path diberikan
    if relative_path:
        full_path = os.path.join(base_path, relative_path)
        # Buat parent directory jika belum ada
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path
    
    return base_path