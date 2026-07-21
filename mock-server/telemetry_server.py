#!/usr/bin/env python3
"""
Mock GCS Telemetri Sunucusu.

Gercek bir Yer Kontrol Istasyonu (GCS) sunucusunun yerini tutan, sadece
standart kutuphane kullanan tek dosyalik bir HTTP sunucusu. Unity tarafindaki
TelemetryClient.cs, GET /telemetry istegiyle bu sunucudan anlik ucus verisi
ceker; sunucu, bir ucagin dairesel bir rota uzerinde ucusunu simule eder.

Kullanim:
    python3 telemetry_server.py [port]
"""
import json
import math
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CENTER_LAT = 39.9255
CENTER_LON = 32.8663
RADIUS_DEG = 0.01
ORBIT_PERIOD_SECONDS = 60.0
START_TIME = time.time()


def compute_state(elapsed):
    # Zamana bagli tek gercek kaynagi: hem canli sunucu hem de
    # tools/preview_telemetry.py bu fonksiyonu kullanir, boylece onizleme
    # gorseli sunucunun urettigi degerlerle birebir aynidir.
    angle = (elapsed / ORBIT_PERIOD_SECONDS) * 2 * math.pi

    latitude = CENTER_LAT + RADIUS_DEG * math.sin(angle)
    longitude = CENTER_LON + RADIUS_DEG * math.cos(angle)
    heading = (math.degrees(-angle) + 90) % 360

    altitude = 1000 + 150 * math.sin(elapsed / 15.0)
    speed = 120 + 10 * math.sin(elapsed / 8.0)
    battery = max(20.0, 100.0 - (elapsed % 1800) / 18.0)
    status = "LOITER" if int(elapsed / 20) % 3 == 0 else "CRUISE"

    return {
        "aircraftId": "TB2-01",
        "elapsedSeconds": elapsed,
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "altitudeMeters": round(altitude, 1),
        "speedKmh": round(speed, 1),
        "headingDegrees": round(heading, 1),
        "batteryPercent": round(battery, 1),
        "status": status,
        "linkQuality": round(0.85 + 0.1 * math.sin(elapsed / 5.0), 2),
    }


def build_telemetry():
    state = compute_state(time.time() - START_TIME)
    state["timestampUtc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    del state["elapsedSeconds"]
    return state


class TelemetryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/telemetry"):
            payload = json.dumps(build_telemetry()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = ThreadingHTTPServer(("0.0.0.0", port), TelemetryHandler)
    print(f"Mock telemetri sunucusu calisiyor: http://localhost:{port}/telemetry")
    print("Durdurmak icin Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
