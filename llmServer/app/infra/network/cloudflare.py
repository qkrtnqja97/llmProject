# llmServer/app/infra/network/cloudflare.py

import subprocess
import time

class CloudflareTunnel:

    def __init__(self, hostname:str, db_host: str, db_port: int):
        self.hostname = hostname
        self.db_host = db_host
        self.db_port = db_port
        self._proc = None

    def start(self, wait_sec: int = 3):
        subprocess.run(["pkill", "-f", "cloudflared"], stderr=subprocess.DEVNULL)

        cmd = [
            "/usr/local/bin/cloudflared",
            "access",
            "tcp",
            "--hostname",
            self.hostname,
            "--url",
            f"tcp://{self.db_host}:{self.db_port}",
        ]

        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        time.sleep(wait_sec)
        print("✅ Cloudflare 터널 시작")

    def stop(self):
        if self._proc:
            self._proc.terminate()
            print("🔒 Cloudflare 터널 종료")