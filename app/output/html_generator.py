"""Generates offline-first retro HTML newspaper and Markdown editions of the Sloth Gazette."""

from pathlib import Path
from typing import Tuple
from app.parser.schemas import GazettePayload


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{edition_title} — {gazette_date}</title>
    <style>
        :root {{
            --bg-color: #fbf9f4;
            --paper-color: #ffffff;
            --ink-color: #1a1a1a;
            --accent-gold: #b45309;
            --accent-green: #15803d;
            --border-color: #27272a;
            --tag-bg: #f3f4f6;
            --border-light: #e5e7eb;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--ink-color);
            font-family: "Georgia", "Times New Roman", serif;
            line-height: 1.6;
            padding: 30px 20px;
        }}
        .newspaper-container {{
            max-width: 960px;
            margin: 0 auto;
            background: var(--paper-color);
            border: 3px double var(--border-color);
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        }}
        header.masthead {{
            text-align: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .masthead-top {{
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #555;
            margin-bottom: 10px;
        }}
        h1.gazette-title {{
            font-size: 44px;
            font-weight: 900;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin: 10px 0;
            border-top: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 0;
        }}
        .masthead-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-style: italic;
            color: #444;
            margin-top: 8px;
        }}
        .badge-banner {{
            background: #fefce8;
            border: 1px solid #fde047;
            border-left: 6px solid var(--accent-gold);
            padding: 16px 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .badge-title {{
            font-weight: bold;
            font-size: 16px;
            color: var(--accent-gold);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
        }}
        .badge-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            font-size: 14px;
            color: #333;
        }}
        .badge-metric {{
            font-weight: bold;
            color: var(--accent-green);
        }}
        .section-header {{
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 6px;
            margin: 30px 0 20px 0;
            font-weight: 800;
        }}
        .big-moves-grid {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .move-card {{
            border-bottom: 1px dotted var(--border-light);
            padding-bottom: 18px;
        }}
        .move-headline {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .source-tags {{
            display: inline-block;
            background: #ede9fe;
            color: #5b21b6;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 2px 8px;
            border-radius: 3px;
            margin-bottom: 10px;
        }}
        .move-summary {{
            font-size: 16px;
            color: #27272a;
            margin-bottom: 8px;
        }}
        .move-impact {{
            font-size: 14px;
            color: var(--accent-green);
            font-style: italic;
        }}
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }}
        @media (max-width: 768px) {{
            .two-column {{
                grid-template-columns: 1fr;
            }}
            h1.gazette-title {{
                font-size: 28px;
            }}
        }}
        .radar-list {{
            list-style: none;
        }}
        .radar-item {{
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #f1f5f9;
        }}
        .radar-name {{
            font-weight: bold;
            font-size: 16px;
            color: #1e3a8a;
        }}
        .radar-url {{
            font-size: 12px;
            color: #64748b;
            font-family: monospace;
        }}
        .radar-desc {{
            font-size: 14px;
            margin-top: 4px;
        }}
        .concept-box {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            padding: 20px;
            border-radius: 4px;
        }}
        .concept-title {{
            font-size: 18px;
            font-weight: bold;
            color: var(--accent-green);
            margin-bottom: 10px;
        }}
        .concept-text {{
            font-size: 15px;
            color: #1e293b;
        }}
        footer.paper-footer {{
            text-align: center;
            border-top: 2px solid var(--border-color);
            margin-top: 40px;
            padding-top: 15px;
            font-size: 12px;
            color: #71717a;
        }}
    </style>
</head>
<body>
    <div class="newspaper-container">
        <header class="masthead">
            <div class="masthead-top">The Zero-Effort Morning Gazette • Local-First • 100% On-Device</div>
            <h1 class="gazette-title">{edition_title}</h1>
            <div class="masthead-meta">
                <span>Date: {gazette_date}</span>
                <span>Inference: Local Gemma 2</span>
                <span>Privacy: Zero Bytes Leaked</span>
            </div>
        </header>

        {badge_html}

        <div class="section-header">The Big Moves (Cross-Source Deduplicated)</div>
        <div class="big-moves-grid">
            {big_moves_html}
        </div>

        <div class="two-column">
            <div>
                <div class="section-header">Tool & Repo Radar</div>
                <ul class="radar-list">
                    {radar_html}
                </ul>
            </div>
            <div>
                <div class="section-header">Concept of the Day</div>
                <div class="concept-box">
                    <div class="concept-title">{concept_topic}</div>
                    <p class="concept-text">{concept_explanation}</p>
                </div>
            </div>
        </div>

        <footer class="paper-footer">
            <p>Generated silently while you slept by <strong>Slothreader</strong>. Instrumented with Sentry Agent Tracing.</p>
            <p>Powered by open-weight Google Gemma 2 via Ollama • Never sends email text to external APIs.</p>
        </footer>
    </div>
</body>
</html>
"""


def render_html(gazette: GazettePayload) -> str:
    """Renders a self-contained retro newspaper HTML page."""
    # Build Sloth Badge HTML
    badge_html = ""
    if gazette.metrics:
        m = gazette.metrics
        badge_html = f"""
        <div class="badge-banner">
            <div class="badge-title">🏆 Sloth Badge of Honor: Reading Laziness Rewarded</div>
            <div class="badge-stats">
                <div>Raw Words: <strong>{m.raw_ingested_words:,}</strong></div>
                <div>Noise Removed: <strong>{m.fluff_stripped_words:,} words</strong></div>
                <div>Sponsors Omitted: <strong>{m.sponsors_eliminated} ads</strong></div>
                <div>Compression: <strong>{m.compression_ratio_pct:.1f}%</strong></div>
                <div>Time Saved: <span class="badge-metric">{m.reading_minutes_saved:.0f} Minutes</span></div>
            </div>
        </div>
        """

    # Build Big Moves HTML
    moves_items = []
    for move in gazette.big_moves:
        sources_str = " + ".join(move.sources) if move.sources else "Industry News"
        moves_items.append(f"""
        <div class="move-card">
            <div class="source-tags">{sources_str}</div>
            <div class="move-headline">{move.headline}</div>
            <p class="move-summary">{move.summary}</p>
            <p class="move-impact"><strong>Impact:</strong> {move.technical_impact}</p>
        </div>
        """)
    big_moves_html = "\n".join(moves_items)

    # Build Radar HTML
    radar_items = []
    for item in gazette.tool_radar:
        radar_items.append(f"""
        <li class="radar-item">
            <div class="radar-name">{item.name}</div>
            <div class="radar-url">{item.url_or_ref}</div>
            <div class="radar-desc">{item.one_liner}</div>
        </li>
        """)
    radar_html = "\n".join(radar_items)

    concept_topic = gazette.quick_concept.topic if gazette.quick_concept else "Systems Engineering"
    concept_explanation = gazette.quick_concept.explanation if gazette.quick_concept else "Consolidating engineering knowledge."

    return HTML_TEMPLATE.format(
        edition_title=gazette.edition_title,
        gazette_date=gazette.gazette_date,
        badge_html=badge_html,
        big_moves_html=big_moves_html,
        radar_html=radar_html,
        concept_topic=concept_topic,
        concept_explanation=concept_explanation,
    )


def render_markdown(gazette: GazettePayload) -> str:
    """Renders clean markdown representation of the gazette."""
    lines = [
        f"# {gazette.edition_title}",
        f"> **Date:** {gazette.gazette_date} | **Inference:** Local Gemma 2 | **Privacy:** 100% Local-First\n",
    ]

    if gazette.metrics:
        m = gazette.metrics
        lines.extend([
            "## 🏆 Sloth Badge of Honor",
            f"- **Time Saved:** {m.reading_minutes_saved:.0f} minutes",
            f"- **Raw Ingested Words:** {m.raw_ingested_words:,}",
            f"- **Fluff & Ads Stripped:** {m.fluff_stripped_words:,} words ({m.sponsors_eliminated} sponsor ads eliminated)",
            f"- **Word Compression Ratio:** {m.compression_ratio_pct:.1f}%\n",
        ])

    lines.append("## 📰 The Big Moves (Cross-Source Deduplicated)")
    for idx, move in enumerate(gazette.big_moves, start=1):
        sources = ", ".join(move.sources) if move.sources else "General"
        lines.append(f"### {idx}. {move.headline} `[{sources}]`")
        lines.append(f"{move.summary}\n")
        lines.append(f"**Technical Impact:** {move.technical_impact}\n")

    if gazette.tool_radar:
        lines.append("## 🛠️ Tool & Repo Radar")
        for item in gazette.tool_radar:
            lines.append(f"- **{item.name}** (`{item.url_or_ref}`): {item.one_liner}")
        lines.append("")

    if gazette.quick_concept:
        lines.extend([
            "## 💡 System Design Concept of the Day",
            f"### {gazette.quick_concept.topic}",
            f"{gazette.quick_concept.explanation}\n",
        ])

    return "\n".join(lines)


def save_gazette_files(gazette: GazettePayload, output_dir: Path = None) -> Tuple[Path, Path]:
    """Writes both the Markdown and HTML gazette files to disk."""
    out = output_dir or Path.cwd()
    out.mkdir(parents=True, exist_ok=True)

    md_path = out / f"GAZETTE-{gazette.gazette_date}.md"
    html_path = out / "gazette.html"

    md_path.write_text(render_markdown(gazette), encoding="utf-8")
    html_path.write_text(render_html(gazette), encoding="utf-8")

    return md_path, html_path
