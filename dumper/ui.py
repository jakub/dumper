from pathlib import Path
from typing import Any, Dict, List

import humanize
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def create_file_console(file_path: Path) -> Console:
    return Console(file=open(file_path, "w"), color_system=None)

def indent_text(text: str, indent: int = 2) -> str:
    return "\n".join(" " * indent + line for line in text.split("\n"))

def display_header(console: Console, args: Any) -> None:
    header = f"""
[bold magenta]d u m p e r[/bold magenta]
[white]{'Input':<15}[/white] [bright_cyan]{str(args.input_path)}[/bright_cyan]
[white]{'Output':<15}[/white] [bright_cyan]{str(args.output)}[/bright_cyan]
[white]{'File Extension':<15}[/white] [bright_cyan]{args.ext or 'All files'}[/bright_cyan]
[white]{'Split Size':<15}[/white] [bright_cyan]{humanize.intcomma(args.split) if args.split else 'N/A'}[/bright_cyan]
"""
    console.print(indent_text(header))

def display_results(console: Console, results: Dict[str, Any]) -> None:
    dedup_rate = (1 - results['unique_credentials'] / results['total_credentials']) * 100
    failed_files_count = len(results['failed_files'])
    results_text = f"""
[bold magenta]Processing Results[/bold magenta]
[white]{'Total Files Processed':<25}[/white] [bright_cyan]{humanize.intcomma(results['total_files'])}[/bright_cyan]
[white]{'Failed Files':<25}[/white] [bright_cyan]{humanize.intcomma(failed_files_count)}[/bright_cyan]
[white]{'Total Credentials Found':<25}[/white] [bright_cyan]{humanize.intcomma(results['total_credentials'])}[/bright_cyan]
[white]{'Unique Credentials':<25}[/white] [bright_cyan]{humanize.intcomma(results['unique_credentials'])}[/bright_cyan]
[white]{'Deduplication Rate':<25}[/white] [bright_cyan]{dedup_rate:.2f}%[/bright_cyan]
"""
    console.print(indent_text(results_text))

    if failed_files_count > 0:
        display_failed_files(console, results['failed_files'])

def display_failed_files(console: Console, failed_files: List[Dict[str, Any]]) -> None:
    console.print("\n[bold red]Failed Files:[/bold red]")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File Path", style="cyan", width=50)
    table.add_column("Error", style="red", width=30)
    table.add_column("Sample", style="yellow")

    for file in failed_files:
        table.add_row(
            str(file['file_path']),
            file['error'],
            file['sample'].replace('\n', '\\n')
        )

    console.print(table)

def log_processed_file(console: Console, file_result: Dict[str, Any], input_path: Path) -> None:
    file_path = Path(file_result['file_path'])
    relative_path = str(file_path.relative_to(input_path))
    if len(relative_path) > 50:
        relative_path = relative_path[:47] + "..."
    file_size = humanize.naturalsize(file_result['file_size'])
    total_lines = humanize.intcomma(file_result['total_lines'])
    time_taken = f"{file_result['time_taken']:.2f}s"

    log_text = (
        f"[white]{relative_path:<53}[/] "
        f"[blue]{file_size:>12}[/]"
        f"[green]{total_lines:>10} lines[/]"
        f"[yellow]{time_taken:>8}[/]"
    )
    console.print(indent_text(log_text))
