#!/usr/bin/env python3
"""
mock-server/telemetry_server.py'deki compute_state(elapsed) fonksiyonunu
(sunucuyla birebir ayni kod) zaman icinde orneklyerek uc parcali bir
onizleme uretir: ucus rotasi (enlem/boylam), irtifa/hiz zaman serisi ve
OperatorPanelUI.cs'deki alan duzenini yansitan bir panel mockup'i.

Durust not: Panel gorseli bir Unity Canvas ekran goruntusu degildir —
Unity Editor bu gelistirme ortaminda mevcut olmadigi icin OperatorPanelUI.cs
ile ayni alan/duzen mantigini yansitan, elle cizilmis bir mockup'tir.
Rota ve zaman serisi grafikleri ise gercekten sunucunun urettigi degerlerdir.

Kullanim:
    python3 preview_telemetry.py --out ../docs/telemetry_preview.png
"""
import argparse
import importlib.util
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def load_server_module():
    path = os.path.join(os.path.dirname(__file__), "..", "mock-server", "telemetry_server.py")
    spec = importlib.util.spec_from_file_location("telemetry_server", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def draw_flight_path(server, duration, steps, size, font_title, font_label):
    img = Image.new("RGB", (size, size), (14, 18, 24))
    draw = ImageDraw.Draw(img, "RGBA")

    states = [server.compute_state(t) for t in
              [duration * i / (steps - 1) for i in range(steps)]]

    def to_px(lat, lon):
        x = (lon - server.CENTER_LON) / (server.RADIUS_DEG * 1.4) * (size / 2) + size / 2
        y = (lat - server.CENTER_LAT) / (server.RADIUS_DEG * 1.4) * (size / 2) + size / 2
        return x, size - y

    pts = [to_px(s["latitude"], s["longitude"]) for s in states]
    for i in range(len(pts) - 1):
        t = i / max(len(pts) - 2, 1)
        color = (60 + int(120 * t), 160, 240 - int(80 * t), 255)
        draw.line([pts[i], pts[i + 1]], fill=color, width=3)

    draw.ellipse([pts[0][0] - 6, pts[0][1] - 6, pts[0][0] + 6, pts[0][1] + 6], fill=(70, 220, 90, 255))
    draw.ellipse([pts[-1][0] - 6, pts[-1][1] - 6, pts[-1][0] + 6, pts[-1][1] + 6], fill=(230, 60, 60, 255))

    draw.rectangle([0, 0, size, 40], fill=(10, 10, 10, 190))
    draw.text((10, 4), "Ucus Rotasi (enlem/boylam)", fill=(255, 255, 255, 255), font=font_title)
    draw.text((10, 22), f"{duration:.0f}s, {server.ORBIT_PERIOD_SECONDS:.0f}s yorunge periyodu", fill=(200, 200, 200, 255), font=font_label)
    return img, states


def draw_timeseries(states, size_w, size_h, font_title, font_label):
    img = Image.new("RGB", (size_w, size_h), (14, 18, 24))
    draw = ImageDraw.Draw(img)

    times = [s["elapsedSeconds"] for s in states]
    alts = [s["altitudeMeters"] for s in states]
    speeds = [s["speedKmh"] for s in states]

    pad_l, pad_r, pad_t, pad_b = 50, 20, 46, 30
    plot_w = size_w - pad_l - pad_r
    plot_h = size_h - pad_t - pad_b

    def scaled(values, y0, y1):
        vmin, vmax = min(values), max(values)
        vmin -= (vmax - vmin) * 0.15 or 1
        vmax += (vmax - vmin) * 0.15 or 1
        return [y1 - (v - vmin) / (vmax - vmin) * (y1 - y0) for v in values]

    xs = [pad_l + (t / times[-1]) * plot_w for t in times]

    draw.rectangle([pad_l, pad_t, pad_l + plot_w, pad_t + plot_h], outline=(70, 70, 80, 255))
    for frac in (0.25, 0.5, 0.75):
        y = pad_t + plot_h * frac
        draw.line([(pad_l, y), (pad_l + plot_w, y)], fill=(40, 44, 52, 255))

    alt_ys = scaled(alts, pad_t, pad_t + plot_h)
    draw.line(list(zip(xs, alt_ys)), fill=(90, 190, 255, 255), width=3)

    speed_ys = scaled(speeds, pad_t, pad_t + plot_h)
    draw.line(list(zip(xs, speed_ys)), fill=(255, 170, 60, 255), width=3)

    draw.rectangle([0, 0, size_w, 40], fill=(10, 10, 10, 190))
    draw.text((10, 4), "Irtifa & Hiz - Zaman Serisi (gercek sunucu ciktisi)", fill=(255, 255, 255, 255), font=font_title)
    draw.text((10, 22), f"Irtifa: {min(alts):.0f}-{max(alts):.0f} m    Hiz: {min(speeds):.0f}-{max(speeds):.0f} km/h", fill=(200, 200, 200, 255), font=font_label)

    draw.rectangle([pad_l, size_h - 16, pad_l + 12, size_h - 6], fill=(90, 190, 255, 255))
    draw.text((pad_l + 18, size_h - 18), "Irtifa (m)", fill=(220, 220, 220, 255), font=font_label)
    draw.rectangle([pad_l + 110, size_h - 16, pad_l + 122, size_h - 6], fill=(255, 170, 60, 255))
    draw.text((pad_l + 128, size_h - 18), "Hiz (km/h)", fill=(220, 220, 220, 255), font=font_label)
    return img


def draw_panel_mockup(sample, size_w, size_h, font_title, font_label, font_value):
    img = Image.new("RGB", (size_w, size_h), (18, 22, 28))
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle([0, 0, size_w, 40], fill=(10, 10, 10, 190))
    draw.text((10, 4), "OperatorPanelUI - Alan Duzeni Mockup'i", fill=(255, 255, 255, 255), font=font_title)
    draw.text((10, 22), "(Unity Canvas ekran goruntusu degil - alan/duzen onizlemesi)", fill=(200, 200, 200, 255), font=font_label)

    # Ust durum satiri: pusula (HeadingNeedle) solda, LinkStatusIndicator sag ustte.
    status_top, status_h = 52, 118
    link_color = (70, 220, 90, 255)
    draw.ellipse([size_w - 30, status_top, size_w - 16, status_top + 14], fill=link_color)
    draw.text((size_w - 150, status_top), "LinkStatusIndicator", fill=(160, 160, 170, 255), font=font_label)

    cx, cy, r = 70, status_top + status_h // 2 + 6, 42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(90, 100, 115, 255), width=2)
    rad = math.radians(sample["headingDegrees"])
    tip = (cx + math.sin(rad) * r * 0.85, cy - math.cos(rad) * r * 0.85)
    draw.line([(cx, cy), tip], fill=(90, 190, 255, 255), width=3)
    draw.text((cx - 36, cy + r + 6), "HeadingNeedle", fill=(160, 160, 170, 255), font=font_label)

    battery = sample.get("batteryPercent", 100)
    bx, by, bw, bh = 150, status_top + 10, size_w - 150 - 24, 20
    draw.rectangle([bx, by, bx + bw, by + bh], outline=(90, 100, 115, 255))
    draw.rectangle([bx, by, bx + bw * (battery / 100.0), by + bh], fill=(90, 220, 120, 255))
    draw.text((bx, by + bh + 4), f"BatteryFill {battery:.0f}%", fill=(160, 160, 170, 255), font=font_label)

    fields = [
        ("AIRCRAFT ID", sample["aircraftId"]),
        ("KONUM", f"{sample['latitude']:.4f}, {sample['longitude']:.4f}"),
        ("IRTIFA", f"{sample['altitudeMeters']:.0f} m"),
        ("HIZ", f"{sample['speedKmh']:.0f} km/h"),
        ("YON", f"{sample['headingDegrees']:.0f} deg"),
        ("DURUM", sample["status"]),
    ]

    field_h, field_gap = 46, 8
    y = status_top + status_h + 10
    for label, value in fields:
        draw.rectangle([16, y, size_w - 16, y + field_h], outline=(60, 66, 76, 255), fill=(26, 30, 38, 255))
        draw.text((28, y + 6), label, fill=(140, 150, 165, 255), font=font_label)
        draw.text((28, y + 22), str(value), fill=(240, 240, 245, 255), font=font_value)
        y += field_h + field_gap

    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../docs/telemetry_preview.png")
    parser.add_argument("--duration", type=float, default=90.0)
    parser.add_argument("--steps", type=int, default=180)
    args = parser.parse_args()

    server = load_server_module()

    try:
        font_title = ImageFont.load_default(size=15)
        font_label = ImageFont.load_default(size=12)
        font_value = ImageFont.load_default(size=16)
    except TypeError:
        font_title = font_label = font_value = ImageFont.load_default()

    path_img, states = draw_flight_path(server, args.duration, args.steps, 320, font_title, font_label)
    ts_img = draw_timeseries(states, 460, 520, font_title, font_label)
    panel_img = draw_panel_mockup(states[len(states) // 3], 300, 520, font_title, font_label, font_value)

    gap = 14
    combo_w = path_img.width + gap + ts_img.width + gap + panel_img.width
    combo_h = max(path_img.height, ts_img.height, panel_img.height) + 44
    combo = Image.new("RGB", (combo_w, combo_h), (10, 10, 12))
    x = 0
    for im in (path_img, ts_img, panel_img):
        combo.paste(im, (x, 44))
        x += im.width + gap

    draw = ImageDraw.Draw(combo)
    draw.text((10, 12), "Dinamik Telemetri ve Gorev On Izleme Paneli - Python Referans Onizlemesi",
               fill=(255, 255, 255), font=font_title)

    combo.save(args.out)
    print(f"Kaydedildi: {args.out}")


if __name__ == "__main__":
    main()
