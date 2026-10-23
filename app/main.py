"""Main CLI entrypoint for Slothreader."""

import argparse
from pathlib import Path
import sys
from typing import List, Optional

from rich.console import Console
from rich.table import Table

from app.config import settings
from app.engine.gemma_client import GemmaClient
from app.ingest.imap_client import SafeImapClient
from app.ingest.local_loader import LocalNewsletterLoader
from app.output.html_generator import save_gazette_files
from app.output.tui_view import display_gazette
from app.parser.fluff_stripper import FluffStripper
from app.parser.schemas import CleanedArticle, GazettePayload, RawEmail
from app.telemetry.sentry_tracer import tracer


# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(force_terminal=True)


def print_banner():
    """Prints a friendly Slothreader CLI banner."""
    console.print(
        "[bold green]Slothreader[/bold green] — [italic]The zero-effort morning gazette that rewards information laziness.[/italic]\n"
    )


def run_pipeline(
    demo_mode: bool = True,
    live_mode: bool = False,
    skip_llm: bool = False,
    use_mock: bool = False,
    model_override: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Optional[GazettePayload]:
    """Executes the complete Slothreader pipeline with Sentry Agent Tracing."""
    print_banner()

    # Stage 1: Ingestion Layer
    raw_emails: List[RawEmail] = []
    with tracer.start_span(op="email.fetch", description="Fetch newsletters"):
        if live_mode:
            console.print("[cyan]Connecting to IMAP inbox over TLS (read-only)...[/cyan]")
            imap_client = SafeImapClient(settings)
            raw_emails = imap_client.fetch_unread_newsletters()
            console.print(f"[green]✓ Fetched {len(raw_emails)} unread newsletters from inbox.[/green]")
        else:
            console.print("[cyan]Loading bundled demo newsletters for offline evaluation...[/cyan]")
            loader = LocalNewsletterLoader()
            raw_emails = loader.load_demo_newsletters()
            console.print(f"[green]✓ Loaded {len(raw_emails)} bundled sample newsletters.[/green]")

    if not raw_emails:
        console.print("[yellow]No newsletters found to process.[/yellow]")
        return None

    # Stage 2: Deterministic Fluff Stripping
    console.print("[cyan]Running deterministic fluff stripper (removing sponsors, footers & tracking pixels)...[/cyan]")
    stripper = FluffStripper()
    cleaned_articles: List[CleanedArticle] = []

    with tracer.start_span(
        op="email.clean",
        description="Deterministic DOM & Sponsor Stripping",
        data={
            "raw_emails_count": len(raw_emails),
            "total_raw_words": sum(e.raw_word_count for e in raw_emails),
        }
    ) as span:
        for email_item in raw_emails:
            cleaned = stripper.clean_email(email_item)
            cleaned_articles.append(cleaned)
        span["data"]["total_cleaned_words"] = sum(a.cleaned_word_count for a in cleaned_articles)
        span["data"]["sponsors_removed"] = sum(a.sponsors_removed for a in cleaned_articles)

    # Ingestion & Stripping Summary Table
    table = Table(title="Slothreader: Ingestion & Fluff Stripping Summary", show_header=True, header_style="bold magenta")
    table.add_column("Publisher / Source", style="cyan")
    table.add_column("Original Words", justify="right")
    table.add_column("Cleaned Words", justify="right")
    table.add_column("Sponsors Dropped", justify="right", style="green")
    table.add_column("Noise Reduction", justify="right", style="bold yellow")

    total_raw = sum(a.raw_word_count for a in cleaned_articles)
    total_clean = sum(a.cleaned_word_count for a in cleaned_articles)
    total_sponsors = sum(a.sponsors_removed for a in cleaned_articles)

    for a in cleaned_articles:
        reduction_pct = ((a.raw_word_count - a.cleaned_word_count) / a.raw_word_count * 100) if a.raw_word_count else 0
        table.add_row(
            a.source,
            str(a.raw_word_count),
            str(a.cleaned_word_count),
            str(a.sponsors_removed),
            f"{reduction_pct:.1f}%",
        )

    overall_reduction = ((total_raw - total_clean) / total_raw * 100) if total_raw else 0
    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_raw}[/bold]",
        f"[bold]{total_clean}[/bold]",
        f"[bold green]{total_sponsors}[/bold green]",
        f"[bold yellow]{overall_reduction:.1f}%[/bold yellow]",
    )

    console.print(table)
    console.print(f"[dim]Total raw words: {total_raw} → Clean words: {total_clean} ({total_sponsors} sponsor ads eliminated)[/dim]\n")

    if skip_llm:
        console.print("[dim]Skipping LLM synthesis stage (--no-llm specified).[/dim]")
        return None

    # Stage 3: Gemma 2 Deduplication Engine
    gemma = GemmaClient()
    resolved_model = model_override or gemma.resolve_model()
    gazette: Optional[GazettePayload] = None

    if use_mock:
        console.print("[yellow]Using instant offline deterministic synthesis (--mock specified)...[/yellow]")
        gazette, meta = gemma.mock_deduplicate(cleaned_articles)
    else:
        console.print(f"[cyan]Synthesizing and deduplicating cross-newsletter stories with local [bold green]{resolved_model}[/bold green]...[/cyan]")
        with tracer.start_span(
            op="ai.gemma.deduplicate",
            description=f"Gemma deduplication via {resolved_model}",
            data={
                "ai.model": resolved_model,
                "articles_count": len(cleaned_articles),
                "input_words": total_clean,
            }
        ) as span:
            try:
                gazette, meta = gemma.deduplicate(cleaned_articles, model_override=resolved_model)
                span["data"]["duration_seconds"] = meta.get("duration_seconds", 0.0)
                span["data"]["eval_count"] = meta.get("eval_count", 0)
            except Exception as e:
                console.print(f"[yellow]Ollama inference note: {e}[/yellow]")
                console.print("[cyan]Switching to offline fallback digest...[/cyan]")
                gazette, meta = gemma.mock_deduplicate(cleaned_articles)

    # Stage 4: Gazette Output Presentation & Publishing
    with tracer.start_span(op="gazette.render", description="Publish terminal TUI and offline HTML/MD"):
        display_gazette(gazette)
        md_path, html_path = save_gazette_files(gazette, output_dir=output_dir)
        console.print(f"[green]✓ Saved offline Markdown edition:[/green] [bold]{md_path}[/bold]")
        console.print(f"[green]✓ Saved offline Retro HTML newspaper:[/green] [bold]{html_path}[/bold]\n")

    return gazette


def cli_entrypoint():
    """Command-line parser entrypoint."""
    parser = argparse.ArgumentParser(description="Slothreader: Local-first newsletter compiler")
    parser.add_argument("--demo", action="store_true", default=True, help="Run with bundled sample newsletters (default)")
    parser.add_argument("--live", action="store_true", help="Fetch unread emails from configured IMAP account")
    parser.add_argument("--mock", action="store_true", help="Run instant offline mock synthesis without waiting for Ollama")
    parser.add_argument("--model", type=str, default=None, help="Ollama model override (e.g. gemma2:2b, gemma4:e4b)")
    parser.add_argument("--no-llm", action="store_true", help="Run ingestion and fluff stripping only, skip LLM synthesis")

    args = parser.parse_args()
    live_mode = args.live
    demo_mode = not live_mode

    try:
        run_pipeline(
            demo_mode=demo_mode,
            live_mode=live_mode,
            skip_llm=args.no_llm,
            use_mock=args.mock,
            model_override=args.model,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Process cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_entrypoint()
