#!/usr/bin/env python3
"""
AEGIS — Single-Command Launcher
Starts both the FastAPI backend and Streamlit dashboard.
"""

import subprocess
import sys
import time
import os
import signal
import threading

BANNER = """
\033[36m
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║      █████╗ ███████╗ ██████╗ ██╗███████╗                     ║
    ║     ██╔══██╗██╔════╝██╔════╝ ██║██╔════╝                     ║
    ║     ███████║█████╗  ██║  ███╗██║███████╗                     ║
    ║     ██╔══██║██╔══╝  ██║   ██║██║╚════██║                     ║
    ║     ██║  ██║███████╗╚██████╔╝██║███████║                     ║
    ║     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝╚══════╝                     ║
    ║                                                               ║
    ║        Autonomous Risk Governor for Trading Agents            ║
    ║                        v2.0.0                                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
\033[0m"""

def log(msg, color="\033[37m"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"  \033[90m[{timestamp}]\033[0m {color}{msg}\033[0m")

def check_deps():
    missing = []
    for pkg in ["fastapi", "uvicorn", "streamlit", "plotly", "numpy", "pandas"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        log(f"Missing packages: {', '.join(missing)}", "\033[31m")
        log("Installing dependencies...", "\033[33m")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
                       cwd=os.path.dirname(os.path.abspath(__file__)))
        log("Dependencies installed.", "\033[32m")

def stream_output(proc, name, color):
    for line in iter(proc.stdout.readline, b""):
        text = line.decode("utf-8", errors="replace").rstrip()
        if text and "WARNING" not in text and "ScriptRunContext" not in text:
            print(f"  \033[90m[{name}]\033[0m {color}{text}\033[0m")

def main():
    print(BANNER)

    project_dir = os.path.dirname(os.path.abspath(__file__))

    log("Initializing AEGIS systems...", "\033[36m")
    time.sleep(0.3)

    check_deps()

    log("Starting Risk Engine API server...", "\033[33m")
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "aegis.api:app", "--host", "0.0.0.0", "--port", "8000",
         "--log-level", "warning"],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)

    if api_proc.poll() is not None:
        log("API server failed to start!", "\033[31m")
        sys.exit(1)

    log("API server online — http://localhost:8000", "\033[32m")
    time.sleep(0.2)

    log("Starting Dashboard UI...", "\033[33m")
    dashboard_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", os.path.join("aegis", "dashboard.py"),
         "--server.port", "8501",
         "--server.headless", "true",
         "--theme.base", "dark",
         "--browser.gatherUsageStats", "false"],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)

    if dashboard_proc.poll() is not None:
        log("Dashboard failed to start!", "\033[31m")
        api_proc.terminate()
        sys.exit(1)

    log("Dashboard online — http://localhost:8501", "\033[32m")
    time.sleep(0.3)

    # Stream API output in background
    threading.Thread(target=stream_output, args=(api_proc, "API", "\033[90m"), daemon=True).start()
    threading.Thread(target=stream_output, args=(dashboard_proc, "UI ", "\033[90m"), daemon=True).start()

    print()
    print("\033[36m  ════════════════════════════════════════════════════════\033[0m")
    print()
    log("AEGIS is LIVE", "\033[32m")
    print()
    print("  \033[1m\033[37m  Dashboard  →  http://localhost:8501\033[0m")
    print("  \033[1m\033[37m  API        →  http://localhost:8000\033[0m")
    print()
    print("  \033[33m  Click 'RUN DEMO SCENARIO' in the dashboard for the demo.\033[0m")
    print()
    print("\033[36m  ════════════════════════════════════════════════════════\033[0m")
    print()
    log("Press Ctrl+C to shut down all services.", "\033[90m")
    print()

    try:
        while True:
            if api_proc.poll() is not None:
                log("API server stopped unexpectedly.", "\033[31m")
                break
            if dashboard_proc.poll() is not None:
                log("Dashboard stopped unexpectedly.", "\033[31m")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        log("Shutting down AEGIS...", "\033[33m")

    api_proc.terminate()
    dashboard_proc.terminate()

    try:
        api_proc.wait(timeout=5)
        dashboard_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        api_proc.kill()
        dashboard_proc.kill()

    log("All systems offline. Goodbye.", "\033[36m")


if __name__ == "__main__":
    main()
