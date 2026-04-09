#!/usr/bin/env python3
"""Career Ops — Rich terminal dashboard.

Usage:
  python terminal.py             # interactive menu
  python terminal.py overview    # print overview and exit
  python terminal.py apps        # print applications table
  python terminal.py apps 30     # limit to 30 rows
  python terminal.py apps 30 Interview   # filter by status
  python terminal.py pipeline    # show pending pipeline
  python terminal.py check       # interactive duplicate checker
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.columns import Columns
from rich import box

from utils import (
    load_applications, load_pipeline, check_duplicate, update_application,
    STATUSES, STATUS_COLORS,
)

console = Console()

_STATUS_STYLE = {
    "Evaluated": "cyan",
    "Applied":   "blue bold",
    "Responded": "magenta",
    "Interview": "yellow bold",
    "Offer":     "bright_green bold",
    "Rejected":  "red",
    "Discarded": "dim",
    "SKIP":      "dim italic",
}


def _score_style(score) -> str:
    if score is None:
        return "dim"
    s = float(score)
    if s >= 4.5: return "bright_green bold"
    if s >= 4.0: return "green"
    if s >= 3.5: return "yellow"
    return "red"


def _score_str(score) -> str:
    if score is None:
        return "—"
    return f"{float(score):.1f}/5"


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def show_overview():
    apps = load_applications()
    if not apps:
        console.print("[yellow]No applications yet.[/yellow]")
        return

    status_counts: dict[str, int] = {}
    scores = []
    for app in apps:
        s = app.get("status", "Unknown")
        status_counts[s] = status_counts.get(s, 0) + 1
        if app.get("score") is not None:
            scores.append(float(app["score"]))

    avg_score = sum(scores) / len(scores) if scores else None

    # Header panel
    parts = [
        f"Total: [bold]{len(apps)}[/bold]",
        f"Avg Score: [cyan]{avg_score:.1f}/5[/cyan]" if avg_score else "Avg Score: [dim]—[/dim]",
        f"Interviews: [yellow]{status_counts.get('Interview', 0)}[/yellow]",
        f"Offers: [bright_green]{status_counts.get('Offer', 0)}[/bright_green]",
        f"Applied: [blue]{status_counts.get('Applied', 0)}[/blue]",
    ]
    console.print(Panel("  |  ".join(parts), title="[bold cyan]Career Ops[/bold cyan]", border_style="cyan"))

    # Status table
    table = Table(title="Status Breakdown", box=box.ROUNDED, border_style="cyan")
    table.add_column("Status",  style="bold", width=14)
    table.add_column("Count",   justify="right", width=6)
    table.add_column("Bar",     width=32)

    total = len(apps)
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        bar_len = max(1, int(count / total * 28))
        bar = "█" * bar_len
        style = _STATUS_STYLE.get(status, "")
        table.add_row(
            f"[{style}]{status}[/{style}]",
            str(count),
            f"[{style}]{bar}[/{style}]",
        )
    console.print(table)


def show_applications(limit: int = 25, status_filter: str | None = None, search: str | None = None):
    apps = load_applications()

    if status_filter:
        apps = [a for a in apps if a.get("status", "").lower() == status_filter.lower()]
    if search:
        s = search.lower()
        apps = [a for a in apps
                if s in a.get("company", "").lower() or s in a.get("role", "").lower()]

    apps_sorted = sorted(apps, key=lambda x: x.get("date", ""), reverse=True)[:limit]

    table = Table(
        title=f"Applications ({len(apps_sorted)} shown of {len(load_applications())} total)",
        box=box.SIMPLE_HEAD,
        border_style="cyan",
        expand=True,
    )
    table.add_column("#",       style="dim",   width=4)
    table.add_column("Date",                   width=12)
    table.add_column("Company",               width=22)
    table.add_column("Role",                  width=34)
    table.add_column("Score",  justify="right", width=7)
    table.add_column("Status",                width=13)
    table.add_column("Notes",                 width=28)

    for app in apps_sorted:
        score = app.get("score")
        sc_style = _score_style(score)
        status = app.get("status", "—")
        st_style = _STATUS_STYLE.get(status, "")

        table.add_row(
            app.get("id", "—"),
            str(app.get("date", "—"))[:10],
            app.get("company", "—"),
            (app.get("role") or "—")[:34],
            f"[{sc_style}]{_score_str(score)}[/{sc_style}]",
            f"[{st_style}]{status}[/{st_style}]",
            (str(app.get("notes") or ""))[:28],
        )

    console.print(table)


def show_pipeline():
    pipeline = load_pipeline()
    pending = [j for j in pipeline if j["status"] == "pending"]
    done    = [j for j in pipeline if j["status"] == "done"]

    console.print(
        Panel(
            f"Pending: [yellow bold]{len(pending)}[/yellow bold]  |  Done: [green]{len(done)}[/green]",
            title="[bold]Pipeline[/bold]",
            border_style="yellow",
        )
    )

    if not pending:
        console.print("[green]Pipeline is empty — nothing to evaluate.[/green]")
        return

    table = Table(box=box.SIMPLE_HEAD, border_style="yellow")
    table.add_column("Company", width=22)
    table.add_column("Title",   width=36)
    table.add_column("URL",     width=50)
    table.add_column("Dup?",    width=6)

    for job in pending:
        jurl    = job.get("url", "")
        company = job.get("company", "?")
        title   = job.get("title", "?")
        dup     = check_duplicate(url=jurl, company=company)
        dup_tag = "[red]⚠[/red]" if dup["is_duplicate"] else "[green]✓[/green]"
        table.add_row(company, title, jurl[:50], dup_tag)

    console.print(table)


def interactive_duplicate_check():
    console.print("[bold cyan]Duplicate Checker[/bold cyan]")
    url     = Prompt.ask("Job URL (Enter to skip)", default="")
    company = Prompt.ask("Company")
    role    = Prompt.ask("Role (Enter to skip)", default="")

    result = check_duplicate(
        url=url or None,
        company=company,
        role=role or None,
    )

    if result["is_duplicate"]:
        ex = result["existing"]
        console.print(Panel(
            f"[red]⚠ DUPLICATE ({result['match_type']})[/red]\n"
            f"[bold]{ex.get('company')}[/bold] — {ex.get('role')}\n"
            f"Status: {ex.get('status')}  |  Score: {ex.get('score','—')}/5  |  Date: {ex.get('date')}",
            border_style="red",
        ))
    elif result.get("match_type") == "company_exists":
        console.print(f"[yellow]ℹ {result['warning']}[/yellow]")
        for a in result.get("existing", [])[:5]:
            console.print(f"  • {a.get('role','?')} — {a.get('status')}")
    else:
        console.print("[green]✅ No duplicate found — safe to add.[/green]")


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

def interactive_menu():
    while True:
        console.print("\n[bold cyan]Career Ops — Terminal[/bold cyan]")
        console.print("  [1] Overview")
        console.print("  [2] Applications")
        console.print("  [3] Pipeline")
        console.print("  [4] Duplicate check")
        console.print("  [q] Quit")

        choice = Prompt.ask("\nChoice", choices=["1", "2", "3", "4", "q"])

        if choice == "1":
            show_overview()
        elif choice == "2":
            search = Prompt.ask("Search term (Enter to skip)", default="")
            status = Prompt.ask("Status filter (Enter for all)", default="")
            try:
                limit = int(Prompt.ask("Max rows", default="25"))
            except ValueError:
                limit = 25
            show_applications(limit=limit, status_filter=status or None, search=search or None)
        elif choice == "3":
            show_pipeline()
        elif choice == "4":
            interactive_duplicate_check()
        elif choice == "q":
            break


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        interactive_menu()
    elif args[0] == "overview":
        show_overview()
    elif args[0] == "apps":
        limit  = int(args[1]) if len(args) > 1 else 25
        status = args[2]      if len(args) > 2 else None
        search = args[3]      if len(args) > 3 else None
        show_applications(limit=limit, status_filter=status, search=search)
    elif args[0] == "pipeline":
        show_pipeline()
    elif args[0] == "check":
        interactive_duplicate_check()
    else:
        console.print(f"[red]Unknown command: {args[0]}[/red]")
        console.print("Commands: overview | apps [limit] [status] | pipeline | check")
