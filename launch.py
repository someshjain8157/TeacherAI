import socket
import time
import webbrowser
from pathlib import Path
import sys

import uvicorn
import urllib.request
import urllib.error


APP_URL = "http://127.0.0.1:8000"
OLLAMA_URL = "http://127.0.0.1:11434/api/tags"


def wait_for_server(host: str = "127.0.0.1", port: int = 8000, timeout: int = 60) -> bool:
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)

    return False


def ollama_is_running() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA_URL, timeout=2):
            return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def show_error(message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("TeacherAI", message)
        root.destroy()
    except Exception:
        print(message, file=sys.stderr)


if __name__ == "__main__":
    app_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    try:
        if app_dir.exists():
            import os

            os.chdir(app_dir)
    except OSError:
        pass

    if not ollama_is_running():
        show_error(
            "TeacherAI could not start because Ollama is not running.\n\n"
            "Please open Ollama, make sure the model is available, and then run TeacherAI again."
        )
        raise SystemExit(1)

    uvicorn_config = {
        "app": "app.server:app",
        "host": "127.0.0.1",
        "port": 8000,
    }

    # Start the server first, then open the browser once the port is ready.
    import threading

    server_thread = threading.Thread(
        target=uvicorn.run,
        kwargs=uvicorn_config,
    )
    server_thread.start()

    if wait_for_server():
        webbrowser.open(APP_URL)
    else:
        show_error(
            "TeacherAI started, but the local web server did not become ready in time."
        )

    server_thread.join()
