#!/usr/bin/env python3
"""
Generate a sleek, terminal-styled Neofetch info card SVG.
Includes title bar, ASCII system badge, key-value system info rows,
color palette swatch, and animated staggered line-by-line reveal.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

# Dimensions matching aspect ratio with portrait (portrait is 840x885)
CANVAS_W = 1080
CANVAS_H = 1140
PAD = 36
TITLEBAR_H = 46

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"

# Text Colors
ACCENT = "#58a6ff"       # Blue key color
GREEN = "#3fb950"        # Green
YELLOW = "#d29922"       # Gold/Yellow
PURPLE = "#bc8cff"       # Purple
CYAN = "#39c5cf"         # Cyan
TEXT_MAIN = "#e6edf3"    # Bright white/gray
TEXT_MUTED = "#8b949e"   # Muted gray
DIVIDER = "#21262d"

INFO_ROWS = [
    ("OS", "Linux / Azure Cloud Environment", ACCENT),
    ("Host", "BPIT ~ Computer Science & Engineering ('28)", TEXT_MAIN),
    ("Role", "Software & Cloud Engineer · AI Builder", GREEN),
    ("Certs", "Microsoft Azure Fundamentals (AZ-900)", YELLOW),
    ("Stack", "Python · FastAPI · Apache Kafka · Linux", CYAN),
    ("Specialty", "Agentic AI · Microservices · Event Streaming", PURPLE),
    ("Tools", "Docker · Git · GitHub Actions · Azure · Bash", TEXT_MAIN),
    ("Learning", "Distributed Systems & Advanced AI Agents", ACCENT),
    ("Status", "Building high-performance cloud applications", GREEN),
    ("GitHub", "github.com/umang9369", ACCENT),
]

ASCII_LOGO = [
    "      /\\        ",
    "     /  \\       ",
    "    / /\\ \\      ",
    "   / /  \\ \\     ",
    "  / / /\\ \\ \\    ",
    " / / /__\\ \\ \\   ",
    "/_/ /____\\ \\_\\  ",
    "\\_\\/______\\/_/  ",
]

COLOR_SWATCHES_1 = ["#ff5555", "#50fa7b", "#f1fa8c", "#bd93f9", "#ff79c6", "#8be9fd", "#f8f8f2"]
COLOR_SWATCHES_2 = ["#e06c75", "#98c379", "#e5c07b", "#61afef", "#c678dd", "#56b6c2", "#abb2bf"]


def build_svg():
    css = """
@keyframes fadeInLine {
  0% { opacity: 0; transform: translateY(4px); }
  100% { opacity: 1; transform: translateY(0); }
}
.term-line {
  opacity: 0;
  animation: fadeInLine 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
"""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, \'Liberation Mono\', monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="cardBg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0%" stop-color="{BG2}"/>',
        f'<stop offset="100%" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',

        # Window background & border
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="14" fill="url(#cardBg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="14" fill="none" stroke="{FRAME}" stroke-width="1.5"/>',

        # Title bar
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1.5"/>',
    ]

    # macOS window buttons
    for i, col in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i * 22}" cy="{TITLEBAR_H / 2}" r="7" fill="{col}"/>')

    # Title text
    parts.append(
        f'<text x="{CANVAS_W / 2}" y="{TITLEBAR_H / 2 + 5}" fill="{TITLE_TEXT}" font-size="16" '
        f'font-weight="500" text-anchor="middle">umang@github: ~$ neofetch --profile</text>'
    )

    # Main content layout
    content_y = TITLEBAR_H + 50
    logo_x = PAD + 20
    info_x = PAD + 280

    # Header user@host
    parts.append(
        f'<g class="term-line" style="animation-delay: 0.1s;">'
        f'<text x="{info_x}" y="{content_y}" font-size="24" font-weight="700">'
        f'<tspan fill="{CYAN}">umang</tspan>'
        f'<tspan fill="{TEXT_MUTED}">@</tspan>'
        f'<tspan fill="{PURPLE}">cloud-dev</tspan>'
        f'</text>'
        f'<line x1="{info_x}" y1="{content_y + 12}" x2="{CANVAS_W - PAD - 30}" y2="{content_y + 12}" '
        f'stroke="{DIVIDER}" stroke-width="2"/>'
        f'</g>'
    )

    # ASCII Logo
    logo_y = content_y + 50
    for idx, line in enumerate(ASCII_LOGO):
        delay = 0.15 + idx * 0.05
        parts.append(
            f'<text class="term-line" x="{logo_x}" y="{logo_y + idx * 30}" fill="{CYAN}" '
            f'font-size="20" font-weight="bold" xml:space="preserve" '
            f'style="animation-delay: {delay:.2f}s;">{line}</text>'
        )

    # Info Key/Value rows
    row_start_y = content_y + 50
    line_gap = 48
    for idx, (k, v, val_color) in enumerate(INFO_ROWS):
        curr_y = row_start_y + idx * line_gap
        delay = 0.25 + idx * 0.08
        safe_k = html.escape(k.ljust(11))
        safe_v = html.escape(v)
        parts.append(
            f'<g class="term-line" style="animation-delay: {delay:.2f}s;">'
            f'<text x="{info_x}" y="{curr_y}" font-size="18" font-weight="600" fill="{ACCENT}">{safe_k}</text>'
            f'<text x="{info_x + 130}" y="{curr_y}" font-size="18" fill="{TEXT_MUTED}">› </text>'
            f'<text x="{info_x + 155}" y="{curr_y}" font-size="18" fill="{val_color}" font-weight="500">{safe_v}</text>'
            f'</g>'
        )

    # Color swatches
    swatch_y = row_start_y + len(INFO_ROWS) * line_gap + 40
    swatch_w = 42
    swatch_h = 24
    swatch_gap = 8
    swatch_start_x = info_x

    parts.append(
        f'<g class="term-line" style="animation-delay: 1.1s;">'
        f'<line x1="{info_x}" y1="{swatch_y - 24}" x2="{CANVAS_W - PAD - 30}" y2="{swatch_y - 24}" stroke="{DIVIDER}" stroke-width="2"/>'
    )

    for i, hex_c in enumerate(COLOR_SWATCHES_1):
        parts.append(
            f'<rect x="{swatch_start_x + i * (swatch_w + swatch_gap)}" y="{swatch_y}" '
            f'width="{swatch_w}" height="{swatch_h}" rx="4" fill="{hex_c}"/>'
        )

    for i, hex_c in enumerate(COLOR_SWATCHES_2):
        parts.append(
            f'<rect x="{swatch_start_x + i * (swatch_w + swatch_gap)}" y="{swatch_y + swatch_h + 8}" '
            f'width="{swatch_w}" height="{swatch_h}" rx="4" fill="{hex_c}"/>'
        )

    parts.append('</g>')

    # Terminal prompt footer
    footer_y = CANVAS_H - 35
    parts.append(
        f'<line x1="0" y1="{footer_y - 20}" x2="{CANVAS_W}" y2="{footer_y - 20}" stroke="{FRAME}" stroke-width="1.5"/>'
        f'<text x="{PAD}" y="{footer_y}" fill="{TITLE_TEXT}" font-size="16">'
        f'umang@github:~$ <tspan fill="{GREEN}">status</tspan> <tspan fill="{TEXT_MAIN}">ready to build &amp; collaborate</tspan>'
        f'</text>'
        f'<rect x="{PAD + 520}" y="{footer_y - 14}" width="10" height="18" fill="{TEXT_MAIN}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
        f'</rect>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main():
    svg = build_svg()
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote Neofetch card to {OUT} ({len(svg)} bytes; {CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
