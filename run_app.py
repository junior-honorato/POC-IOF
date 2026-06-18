import streamlit.runtime.scriptrunner.magic_funcs
import streamlit.web.cli as stcli
import os
import sys

def resolve_path(path):
    """Helper to resolve paths for bundled files."""
    if getattr(sys, "frozen", False):
        # If running as an executable
        basedir = sys._MEIPASS
    else:
        # If running as a script
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

if __name__ == "__main__":
    app_path = resolve_path("app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
    ]
    
    sys.exit(stcli.main())
