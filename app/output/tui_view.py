"""Rich terminal user interface for displaying The Daily Sloth Gazette."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.parser.schemas import GazettePayload


console = Console(force_terminal=True)


def display_gazette(gazette: GazettePayload):
    """Renders The Daily Sloth Gazette to the terminal with Rich styling."""
    console.print()
    
    # 1. Newspaper Masthead
    masthead_text = Text()
    masthead_text.append(f"{gazette.edition_title.upper()}\n", style="bold yellow")
    masthead_text.append(f"Date: {gazette.gazette_date}  •  Offline Morning Edition  •  100% On-Device\n", style="dim italic")
    masthead_panel = Panel(masthead_text, border_style="yellow", padding=(1, 2))
    console.print(masthead_panel)
    console.print()

    # 2. The Big Moves
    console.print("[bold cyan]━━━ THE BIG MOVES (CROSS-SOURCE DEDUPLICATED) ━━━[/bold cyan]\n")
    for idx, move in enumerate(gazette.big_moves, start=1):
        sources_str = " + ".join(move.sources) if move.sources else "Industry"
        console.print(f"[bold white]{idx}. {move.headline}[/bold white] [bold magenta][{sources_str}][/bold magenta]")
        console.print(f"   [dim]{move.summary}[/dim]")
        console.print(f"   [italic green]Impact:[/italic green] {move.technical_impact}\n")

    # 3. Tool & Repo Radar
    if gazette.tool_radar:
        console.print("[bold cyan]━━━ TOOL & REPO RADAR ━━━[/bold cyan]\n")
        radar_table = Table(show_header=True, header_style="bold blue")
        radar_table.add_column("Tool / Project", style="bold white", width=22)
        radar_table.add_column("Reference / Link", style="dim cyan", width=26)
        radar_table.add_column("What It Solves", style="white")

        for item in gazette.tool_radar:
            radar_table.add_row(item.name, item.url_or_ref, item.one_liner)
        console.print(radar_table)
        console.print()

    # 4. Quick Concept
    if gazette.quick_concept:
        concept_panel = Panel(
            f"[bold yellow]{gazette.quick_concept.topic}[/bold yellow]\n\n{gazette.quick_concept.explanation}",
            title="[bold green]💡 System Design Concept of the Day[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(concept_panel)
        console.print()

    # 5. The Sloth Badge of Honor
    if gazette.metrics:
        m = gazette.metrics
        badge_text = Text()
        badge_text.append("SLOTH BADGE OF HONOR: INFORMATION LAZINESS REWARDED\n\n", style="bold yellow")
        badge_text.append(f"• Raw Words Ingested:    {m.raw_ingested_words:,} words\n", style="white")
        badge_text.append(f"• Fluff & Ads Stripped:  {m.fluff_stripped_words:,} words\n", style="white")
        badge_text.append(f"• Final Gazette Size:    {m.gazette_words:,} words\n", style="white")
        badge_text.append(f"• Sponsor Ads Omitted:   {m.sponsors_eliminated} ads\n", style="green")
        badge_text.append(f"• Word Compression:      {m.compression_ratio_pct:.1f}%\n", style="bold cyan")
        badge_text.append(f"\nYOU JUST SAVED APPROXIMATELY {m.reading_minutes_saved:.0f} MINUTES OF READING TODAY!", style="bold green")

        badge_panel = Panel(badge_text, title="[bold gold1]🏆 LAZINESS TROPHY[/bold gold1]", border_style="gold1", padding=(1, 2))
        console.print(badge_panel)
        console.print()
