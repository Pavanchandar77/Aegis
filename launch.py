#!/usr/bin/env python3
"""
AEGIS — Single-Command Launcher (Local Dev)
Starts the FastAPI backend and serves the static dashboard on one port.

Usage:
    python launch.py
"""

import subprocess
import sys
import time
import os
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
    ║                        v3.0.0                                 ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
\033[0m"""


def log(msg, color="\033[37m"):
    timestamp = time.strftime("%H:%M:%S")
    print(f"  \033[90m[{timestamp}]\033[0m {color}{msg}\033[0m")


def check_deps():
    missing = []
    for pkg in ["fastapi", "uvicorn"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        log(f"Missing packages: {', '.join(missing)}", "\033[31m")
        log("Installing dependencies...", "\033[33m")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        log("Dependencies installed.", "\033[32m")


def main():
    print(BANNER)

    project_dir = os.path.dirname(os.path.abspath(__file__))

    log("Initializing AEGIS systems...", "\033[36m")
    time.sleep(0.3)

    check_deps()

    log("Starting AEGIS server (API + Dashboard)...", "\033[33m")

    server_script = os.path.join(project_dir, "serve_local.py")
    proc = subprocess.Popen(
        [sys.executable, server_script],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    time.sleep(2)

    if proc.poll() is not None:
        log("Server failed to start!", "\033[31m")
        out = proc.stdout.read().decode("utf-8", errors="replace")
        if out:
            print(out)
        sys.exit(1)

    # Stream output in background
    def stream(p):
        for line in iter(p.stdout.readline, b""):
            text = line.decode("utf-8", errors="replace").rstrip()
            if text and "WARNING" not in text:
                print(f"  \033[90m[SERVER]\033[0m \033[90m{text}\033[0m")

    threading.Thread(target=stream, args=(proc,), daemon=True).start()

    print()
    print("\033[36m  ════════════════════════════════════════════════════════\033[0m")
    print()
    log("AEGIS is LIVE", "\033[32m")
    print()
    print("  \033[1m\033[37m  Dashboard  →  http://localhost:8000\033[0m")
    print("  \033[1m\033[37m  API        →  http://localhost:8000/api\033[0m")
    print()
    print("  \033[33m  Click 'RUN DEMO SCENARIO' in the dashboard.\033[0m")
    print()
    print("\033[36m  ════════════════════════════════════════════════════════\033[0m")
    print()
    log("Press Ctrl+C to shut down.", "\033[90m")
    print()

    try:
        while True:
            if proc.poll() is not None:
                log("Server stopped unexpectedly.", "\033[31m")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        log("Shutting down AEGIS...", "\033[33m")

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    log("All systems offline. Goodbye.", "\033[36m")


if __name__ == "__main__":
    main()
