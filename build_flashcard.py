# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "edge-tts>=6.1.0",
#   "pypinyin>=0.51.0",
# ]
# ///
"""
Build script for the Chinese Flashcard Web App.

Reads `tu_vung_tieng_trung.md`, auto-fills any missing Pinyin via `pypinyin`,
generates neural female & male MP3 audio via `edge-tts` incrementally,
and embeds the vocabulary dataset into `index.html`.

Usage:
  uv run build_flashcard.py            # Build audio (missing only) + update index.html
  uv run build_flashcard.py --no-audio # Update index.html only (skip TTS)
  uv run build_flashcard.py --check    # Verify data integrity & MP3 coverage
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import edge_tts
from pypinyin import Style, pinyin

BASE_DIR = Path(__file__).resolve().parent
MD_PATH = BASE_DIR / "tu_vung_tieng_trung.md"
HTML_PATH = BASE_DIR / "index.html"
CSV_PATH = BASE_DIR / "tu_vung_google_sheets.csv"
AUDIO_DIR = BASE_DIR / "audio"

FEMALE_VOICE = "zh-CN-XiaoxiaoNeural"
MALE_VOICE = "zh-CN-YunxiNeural"
MIN_MP3_BYTES = 400
MAX_CONCURRENCY = 5
MAX_RETRIES = 4

DATA_START = "/* __VOCAB_DATA_START__ */"
DATA_END = "/* __VOCAB_DATA_END__ */"


def make_audio_id(hanzi: str) -> str:
    return "w_" + hashlib.md5(hanzi.encode("utf-8")).hexdigest()[:10]


def auto_pinyin(hanzi: str) -> str:
    syllables = pinyin(hanzi, style=Style.TONE, heteronym=False)
    return " ".join(item[0] for item in syllables if item)


def parse_markdown(md_path: Path) -> tuple[list[dict], list[str]]:
    if not md_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {md_path}")

    lines = md_path.read_text(encoding="utf-8").splitlines()
    current_group = "Chung"
    seen: dict[str, int] = {}
    cards: list[dict] = []
    warnings: list[str] = []

    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if line.startswith("## "):
            current_group = line[3:].strip()
            continue

        if not (line.startswith("|") and line.endswith("|")):
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue

        # Skip header and separator rows
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if cells[0] in ("Từ (Chữ Hán)", "Từ", "Chữ Hán", "Hanzi"):
            continue

        hanzi = cells[0].strip()
        py = cells[1].strip() if len(cells) > 1 else ""
        meaning = cells[2].strip() if len(cells) > 2 else ""
        example = cells[3].strip() if len(cells) > 3 else ""

        if not hanzi:
            continue
        if not meaning:
            warnings.append(f"Dòng {line_no}: '{hanzi}' bị thiếu nghĩa tiếng Việt.")

        if not py:
            py = auto_pinyin(hanzi)
            warnings.append(f"Dòng {line_no}: '{hanzi}' tự động điền pinyin -> {py}")

        if hanzi in seen:
            warnings.append(
                f"Dòng {line_no}: Trùng từ '{hanzi}' (đã có ở dòng {seen[hanzi]}), bỏ qua bản trùng."
            )
            continue

        seen[hanzi] = line_no
        cards.append(
            {
                "id": len(cards) + 1,
                "audioId": make_audio_id(hanzi),
                "hanzi": hanzi,
                "pinyin": py,
                "meaning": meaning,
                "example": example,
                "group": current_group,
            }
        )

    return cards, warnings


async def synth_one(
    sem: asyncio.Semaphore,
    hanzi: str,
    voice: str,
    out_path: Path,
) -> tuple[bool, str]:
    tmp_path = out_path.with_suffix(".tmp")
    async with sem:
        last_err = ""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                comm = edge_tts.Communicate(hanzi, voice)
                await comm.save(str(tmp_path))
                if tmp_path.exists() and tmp_path.stat().st_size >= MIN_MP3_BYTES:
                    os.replace(tmp_path, out_path)
                    return True, ""
                last_err = "File MP3 rỗng hoặc quá nhỏ"
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            await asyncio.sleep(0.8 * (2 ** (attempt - 1)))
        return False, f"{out_path.name} ({hanzi}, {voice}): {last_err}"


async def generate_missing_audio(cards: list[dict]) -> list[str]:
    female_dir = AUDIO_DIR / "female"
    male_dir = AUDIO_DIR / "male"
    female_dir.mkdir(parents=True, exist_ok=True)
    male_dir.mkdir(parents=True, exist_ok=True)

    tasks_spec: list[tuple[str, str, Path]] = []
    for c in cards:
        aid = c["audioId"]
        f_path = female_dir / f"{aid}.mp3"
        m_path = male_dir / f"{aid}.mp3"
        if not (f_path.exists() and f_path.stat().st_size >= MIN_MP3_BYTES):
            tasks_spec.append((c["hanzi"], FEMALE_VOICE, f_path))
        if not (m_path.exists() and m_path.stat().st_size >= MIN_MP3_BYTES):
            tasks_spec.append((c["hanzi"], MALE_VOICE, m_path))

    if not tasks_spec:
        print("✓ Toàn bộ file âm thanh Nam/Nữ đã có sẵn, không cần tạo thêm.")
        return []

    print(f"Đang tạo {len(tasks_spec)} file âm thanh MP3 (giọng Nữ & Nam)...")
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    coros = [synth_one(sem, hz, v, p) for hz, v, p in tasks_spec]

    errors: list[str] = []
    done = 0
    total = len(coros)
    for fut in asyncio.as_completed(coros):
        ok, err = await fut
        done += 1
        if not ok:
            errors.append(err)
        if done % 40 == 0 or done == total:
            print(f"  Tiến độ audio: {done}/{total} (lỗi: {len(errors)})")
    return errors


def inject_into_html(cards: list[dict]) -> None:
    if not HTML_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy {HTML_PATH}")

    html = HTML_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(DATA_START) + r".*?" + re.escape(DATA_END),
        flags=re.DOTALL,
    )
    if not pattern.search(html):
        raise RuntimeError(
            f"Không tìm thấy marker {DATA_START} ... {DATA_END} trong index.html"
        )

    payload = json.dumps(cards, ensure_ascii=False, separators=(",", ":"))
    replacement = f"{DATA_START}\n    const INITIAL_VOCAB = {payload};\n    {DATA_END}"
    new_html = pattern.sub(lambda _: replacement, html, count=1)
    HTML_PATH.write_text(new_html, encoding="utf-8")


def export_google_sheets_csv(cards: list[dict]) -> None:
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Nhóm", "Từ (Chữ Hán)", "Phiên âm (Pinyin)", "Nghĩa tiếng Việt", "Ví dụ"])
        for c in cards:
            writer.writerow([c["group"], c["hanzi"], c["pinyin"], c["meaning"], c["example"]])


def check_integrity(cards: list[dict], warnings: list[str]) -> int:
    missing_audio = 0
    empty_fields = 0
    for c in cards:
        if not c["hanzi"] or not c["pinyin"] or not c["meaning"]:
            empty_fields += 1
        f_path = AUDIO_DIR / "female" / f"{c['audioId']}.mp3"
        m_path = AUDIO_DIR / "male" / f"{c['audioId']}.mp3"
        if not (f_path.exists() and f_path.stat().st_size >= MIN_MP3_BYTES):
            missing_audio += 1
        if not (m_path.exists() and m_path.stat().st_size >= MIN_MP3_BYTES):
            missing_audio += 1

    groups: dict[str, int] = {}
    for c in cards:
        groups[c["group"]] = groups.get(c["group"], 0) + 1

    print(f"Tổng số từ vựng hợp lệ: {len(cards)}")
    for g, cnt in groups.items():
        print(f"  - {g}: {cnt} từ")
    print(f"Cảnh báo trùng/thiếu khi đọc .md: {len(warnings)}")
    for w in warnings[:15]:
        print("  !", w)
    print(f"Số trường bắt buộc bị trống: {empty_fields}")
    print(f"Số file MP3 Nam/Nữ bị thiếu hoặc lỗi: {missing_audio}")
    return 0 if (empty_fields == 0 and missing_audio == 0 and len(warnings) == 0) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Chinese Flashcard App & Audio")
    parser.add_argument("--no-audio", action="store_true", help="Bỏ qua bước tạo MP3")
    parser.add_argument("--check", action="store_true", help="Chỉ kiểm tra dữ liệu & audio")
    args = parser.parse_args()

    cards, warnings = parse_markdown(MD_PATH)

    if args.check:
        return check_integrity(cards, warnings)

    for w in warnings:
        print("! Cảnh báo:", w)

    if not args.no_audio:
        errors = asyncio.run(generate_missing_audio(cards))
        if errors:
            print(f"⚠ Có {len(errors)} lỗi khi tạo MP3:", file=sys.stderr)
            for e in errors[:10]:
                print("  -", e, file=sys.stderr)
            return 2

    inject_into_html(cards)
    print(f"✓ Đã cập nhật {len(cards)} từ vào {HTML_PATH.name}")
    export_google_sheets_csv(cards)
    print(f"✓ Đã xuất {len(cards)} từ ra {CSV_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
