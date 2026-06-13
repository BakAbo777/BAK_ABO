"""BKS Studio — Desktop shortcut installer for Windows.
Run once after install: python create_shortcut.py
"""
import sys
import os
from pathlib import Path

FACTORY_DIR = Path(__file__).parent.resolve()
START_BAT   = FACTORY_DIR / "start.bat"


def create_windows_shortcut() -> str:
    """Create a .lnk shortcut on the Windows Desktop."""
    try:
        import winshell
        from win32com.client import Dispatch
        desktop = Path(winshell.desktop())
    except ImportError:
        # Fallback: use USERPROFILE
        desktop = Path(os.environ.get("USERPROFILE", "C:/Users/Public")) / "Desktop"

    lnk_path = desktop / "BKS Image Factory.lnk"

    try:
        from win32com.client import Dispatch
        shell    = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(lnk_path))
        shortcut.Targetpath      = str(START_BAT)
        shortcut.WorkingDirectory= str(FACTORY_DIR)
        shortcut.IconLocation    = str(START_BAT)
        shortcut.Description     = "BKS Studio — BAKABO Image Factory v1.1"
        shortcut.save()
        return str(lnk_path)
    except Exception:
        # Ultra-fallback: write a .bat launcher on desktop
        bat = desktop / "BKS Image Factory.bat"
        bat.write_text(f'@echo off\ncall "{START_BAT}"\n')
        return str(bat)


def create_vbs_shortcut() -> str:
    """Create shortcut via VBScript (no extra deps needed on Windows)."""
    desktop  = Path(os.environ.get("USERPROFILE", "C:/Users/Public")) / "Desktop"
    lnk_path = desktop / "BKS Image Factory.lnk"
    vbs = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{lnk_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{START_BAT}"
oLink.WorkingDirectory = "{FACTORY_DIR}"
oLink.Description = "BKS Studio - BAKABO Image Factory v1.1"
oLink.Save
""".strip()
    vbs_tmp = FACTORY_DIR / "_create_shortcut.vbs"
    vbs_tmp.write_text(vbs)
    os.system(f'cscript //nologo "{vbs_tmp}"')
    vbs_tmp.unlink(missing_ok=True)
    return str(lnk_path)


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Shortcut installer is Windows-only.")
        print(f"On macOS/Linux, create an alias to: {START_BAT}")
        sys.exit(0)

    print("Creating desktop shortcut...")
    try:
        path = create_windows_shortcut()
    except Exception:
        path = create_vbs_shortcut()

    if Path(path).exists():
        print(f"✅ Shortcut created: {path}")
    else:
        print(f"⚠️  Could not verify shortcut at: {path}")
        print(f"   Start manually: {START_BAT}")
