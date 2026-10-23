"""Main CLI entrypoint for Slothreader."""

import argparse
import sys
from typing import List

from rich.console import Console
from rich.table import Table

from app.config import settings
from app.ingest.local_loader import LocalNewsletterLoader
from app.ingest.imap_client import SafeImapClient
from app.parser.fluff_stripper import FluffStripper
from app.parser.schemas import RawEmail, CleanedArticle


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


def run_pipeline(demo_mode: bool = True, live_mode: bool = False, skip_llm: bool = False) -> List[CleanedArticle]:
    """Executes the ingestion and fluff-stripping stages."""
    print_banner()

    # Step 1: Ingestion
    raw_emails: List[RawEmail] = []
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
        console.print("[yellow]No newsletters to process. Inbox clean![/yellow]")
        return []

    # Step 2: Deterministic Fluff Stripping
    console.print("[cyan]Running deterministic fluff stripper (removing sponsors, footers & tracking pixels)...[/cyan]")
    stripper = FluffStripper()
    cleaned_articles: List[CleanedArticle] = []

    for email_item in raw_emails:
        cleaned = stripper.clean_email(email_item)
        cleaned_articles.append(cleaned)

    # Print Ingestion & Stripping Summary Table
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

    return cleaned_articles


def cli_entrypoint():
    """Command-line parser entrypoint."""
    parser = argparse.ArgumentParser(description="Slothreader: Local-first newsletter compiler")
    parser.add_argument("--demo", action="store_true", default=True, help="Run with bundled sample newsletters (default)")
    parser.add_argument("--live", action="store_true", help="Fetch unread emails from configured IMAP account")
    parser.add_argument("--model", type=str, default=settings.gemma_model, help="Ollama model name (e.g. gemma2:2b)")
    parser.add_argument("--no-llm", action="store_true", help="Run ingestion and fluff stripping only, skip LLM synthesis")

    args = parser.parse_args()
    live_mode = args.live
    demo_mode = not live_mode

    try:
        run_pipeline(demo_mode=demo_mode, live_mode=live_mode, skip_llm=args.no_llm)
    except KeyboardInterrupt:
        console.print("\n[yellow]Process cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_entrypoint()
