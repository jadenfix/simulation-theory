#!/usr/bin/env python3
"""Render a source-pinned GIF/MP4 for the posterior boundary fix.

The script loads ``inference.py`` directly from two Git revisions, captures the
same boundary calls from both versions, runs the focused tests at the source
revision, and writes a machine-readable receipt next to the media.

Rendering requires Pillow and ffmpeg; neither is part of the mathematical core.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from types import ModuleType

from PIL import Image, ImageDraw, ImageFont


WIDTH = 960
HEIGHT = 540
BACKGROUND = "#0b1020"
PANEL = "#121a2d"
TEXT = "#eef2ff"
MUTED = "#a5b4d4"
RED = "#fb7185"
GREEN = "#4ade80"
BLUE = "#60a5fa"
AMBER = "#fbbf24"


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), text=True).strip()


def load_module(revision: str, destination: Path) -> ModuleType:
    source = subprocess.check_output(
        ("git", "show", f"{revision}:src/simtheory/inference.py"),
        text=True,
    )
    destination.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        f"inference_{revision[:12]}",
        destination,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load inference module at {revision}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture_boundary_results(module: ModuleType) -> list[str]:
    calls = (
        ("posterior(0.9, 1e308)", lambda: module.posterior_from_bayes_factor(0.9, 1e308)),
        ("posterior(0.5, inf)", lambda: module.posterior_from_bayes_factor(0.5, float("inf"))),
        ("posterior(0.5, nan)", lambda: module.posterior_from_bayes_factor(0.5, float("nan"))),
        (
            "interval((0.1, 0.9), (0.5, inf))",
            lambda: module.robust_posterior_interval(
                (0.1, 0.9),
                (0.5, float("inf")),
            ),
        ),
    )
    results: list[str] = []
    for label, call in calls:
        try:
            result = repr(call())
        except Exception as error:  # The exception is part of the captured behavior.
            result = f"{type(error).__name__}: {error}"
        results.append(f"{label}  ->  {result}")
    return results


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    for directory in (
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/dejavu"),
    ):
        path = directory / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def make_frame(
    eyebrow: str,
    title: str,
    lines: list[tuple[str, str]],
    footer: str,
) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    eyebrow_font = load_font(17, bold=True)
    title_font = load_font(32, bold=True)
    body_font = load_font(17)
    footer_font = load_font(14)

    draw.rounded_rectangle((42, 35, WIDTH - 42, HEIGHT - 35), 22, fill=PANEL)
    draw.text((72, 65), eyebrow, font=eyebrow_font, fill=BLUE)
    draw.text((72, 101), title, font=title_font, fill=TEXT)
    draw.line((72, 157, WIDTH - 72, 157), fill="#263552", width=2)

    y = 190
    for line, color in lines:
        wrapped = textwrap.wrap(
            line,
            width=80,
            subsequent_indent="  ",
            break_long_words=False,
            break_on_hyphens=False,
        ) or [""]
        for segment in wrapped:
            draw.text((78, y), segment, font=body_font, fill=color)
            y += 31
        y += 13

    draw.line((72, HEIGHT - 91, WIDTH - 72, HEIGHT - 91), fill="#263552", width=2)
    draw.text((72, HEIGHT - 70), footer, font=footer_font, fill=MUTED)
    return image


def render_media(
    output_dir: Path,
    base_revision: str,
    source_revision: str,
    before: list[str],
    after: list[str],
    test_output: str,
) -> tuple[Path, Path]:
    short_base = base_revision[:12]
    short_source = source_revision[:12]
    frames = [
        make_frame(
            "SOURCE-PINNED NUMERICAL CHECK",
            "Extreme Bayes-factor boundaries",
            [
                (f"BASE    {short_base}", MUTED),
                (f"FIX     {short_source}", GREEN),
                ("Same four calls, loaded directly from each Git revision.", TEXT),
                ("No simulated data and no scientific-evidence claim.", AMBER),
            ],
            "Scope: posterior arithmetic and input validation only",
        ),
        make_frame(
            f"BEFORE · main @ {short_base}",
            "Overflow leaks NaN",
            [(line, RED if "nan" in line.lower() else TEXT) for line in before],
            "Captured from the base revision, not retyped output",
        ),
        make_frame(
            f"AFTER · fix @ {short_source}",
            "Stable limiting behavior",
            [
                (line, GREEN if "1.0" in line else AMBER if "ValueError" in line else TEXT)
                for line in after
            ],
            "Positive infinity is a limit; NaN is rejected",
        ),
        make_frame(
            f"VERIFICATION · fix @ {short_source}",
            "Focused regression suite",
            [
                ("$ python -m pytest tests/test_inference.py", MUTED),
                (test_output, GREEN),
                ("Scientific limitation:", AMBER),
                ("This does not validate a likelihood model or simulation hypothesis.", TEXT),
            ],
            "Exact commands and outputs are preserved in the JSON receipt",
        ),
    ]
    durations_ms = [2400, 4000, 4000, 3400]
    gif_path = output_dir / "posterior-boundary-demo.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations_ms,
        loop=0,
        optimize=True,
    )

    with tempfile.TemporaryDirectory() as temporary:
        temp_dir = Path(temporary)
        concat_lines: list[str] = []
        for index, (frame, duration) in enumerate(zip(frames, durations_ms)):
            frame_path = temp_dir / f"frame-{index}.png"
            frame.save(frame_path)
            concat_lines.extend((f"file '{frame_path}'", f"duration {duration / 1000:.3f}"))
        concat_lines.append(f"file '{temp_dir / f'frame-{len(frames) - 1}.png'}'")
        concat_path = temp_dir / "frames.txt"
        concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
        mp4_path = output_dir / "posterior-boundary-demo.mp4"
        subprocess.run(
            (
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_path),
                "-vf",
                "fps=30,format=yuv420p",
                "-c:v",
                "libx264",
                "-movflags",
                "+faststart",
                str(mp4_path),
            ),
            check=True,
        )
    return gif_path, mp4_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Git revision with the prior behavior")
    parser.add_argument("--source", required=True, help="Git revision containing the fix")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    base_revision = git("rev-parse", f"{args.base}^{{commit}}")
    source_revision = git("rev-parse", f"{args.source}^{{commit}}")
    verified_paths = (
        "src/simtheory/inference.py",
        "tests/test_inference.py",
    )
    source_diff = subprocess.run(
        ("git", "diff", "--quiet", source_revision, "--", *verified_paths),
        check=False,
    )
    if source_diff.returncode != 0:
        raise SystemExit("behavior and test paths must match --source")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        temp_dir = Path(temporary)
        before = capture_boundary_results(
            load_module(base_revision, temp_dir / "inference-before.py")
        )
        after = capture_boundary_results(
            load_module(source_revision, temp_dir / "inference-after.py")
        )

    test_command = (
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        "-o",
        "addopts=",
        "tests/test_inference.py",
    )
    test_run = subprocess.run(
        test_command,
        check=True,
        capture_output=True,
        text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": "src"},
    )
    test_lines = [line.strip() for line in test_run.stdout.splitlines() if line.strip()]
    test_output = test_lines[-1] if test_lines else "tests exited successfully"
    test_stdout_tail = "\n".join(test_lines[-2:]) + "\n"

    gif_path, mp4_path = render_media(
        args.output_dir,
        base_revision,
        source_revision,
        before,
        after,
        test_output,
    )
    receipt = {
        "schema": "posterior-boundary-demo-v1",
        "base_revision": base_revision,
        "source_revision": source_revision,
        "verified_paths": list(verified_paths),
        "captured_calls": [
            "posterior_from_bayes_factor(0.9, 1e308)",
            "posterior_from_bayes_factor(0.5, float('inf'))",
            "posterior_from_bayes_factor(0.5, float('nan'))",
            "robust_posterior_interval((0.1, 0.9), (0.5, float('inf')))",
        ],
        "before": before,
        "after": after,
        "test_command": list(test_command),
        "test_stdout_tail": test_stdout_tail,
        "scientific_limitation": (
            "This demonstrates numerical boundary behavior only; it does not validate "
            "a likelihood model or provide evidence for any simulation hypothesis."
        ),
        "media": [gif_path.name, mp4_path.name],
    }
    receipt_path = args.output_dir / "posterior-boundary-demo-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(gif_path)
    print(mp4_path)
    print(receipt_path)


if __name__ == "__main__":
    main()
