import asyncio
import time
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)

from dumper import IGNORED_FILES
from dumper.output import write_output
from dumper.parser import parse_file
from dumper.ui import log_processed_file


async def process_file(file_path: Path, console: Console, input_path: Path, progress: Progress, task_id: TaskID) -> Dict[str, Any]:
    if file_path.is_dir() or file_path.name in IGNORED_FILES:
        progress.advance(task_id)
        return None

    start_time = asyncio.get_event_loop().time()
    try:
        credentials = await parse_file(str(file_path))
        end_time = asyncio.get_event_loop().time()

        result = {
            "file_path": file_path,
            "credentials": credentials,
            "time_taken": end_time - start_time,
            "total_lines": len(credentials),
            "file_size": file_path.stat().st_size,
            "status": "success"
        }
    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        result = {
            "file_path": file_path,
            "credentials": [],
            "time_taken": end_time - start_time,
            "total_lines": 0,
            "file_size": file_path.stat().st_size,
            "status": "failed",
            "error": str(e),
            "sample": get_file_sample(file_path)
        }

    log_processed_file(console, result, input_path)
    progress.advance(task_id)
    return result

def get_file_sample(file_path: Path, num_lines: int = 3) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return ''.join(f.readline() for _ in range(num_lines))
    except Exception as e:
        return f"Unable to read file: {str(e)}"

async def process_files(args: Any, console: Console) -> Dict[str, Any]:
    input_path = Path(args.input_path)
    output_path = Path(args.output)
    file_extension = args.ext
    split_size = args.split

    files_to_process = []
    if input_path.is_file():
        files_to_process.append(input_path)
    else:
        glob_pattern = f"*.{file_extension}" if file_extension else "*"
        files_to_process = list(input_path.rglob(glob_pattern))

    total_files = len(files_to_process)

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description:<30}"),
        TextColumn("[cyan]{task.completed:>10,} of {task.total:<10,}"),
        BarColumn(bar_width=23),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    )

    with progress:
        # --- Parsing files --- #
        file_task = progress.add_task("[magenta]Processing files...", total=total_files)
        results = await asyncio.gather(*[process_file(file, console, input_path, progress, file_task) for file in files_to_process])
        results = [result for result in results if result is not None]  # collapse this and filter out None results

        all_credentials = []
        failed_files = []
        for result in results:
            if result["status"] == "success":
                all_credentials.extend(result["credentials"])
            else:
                failed_files.append(result)

        total_credentials = len(all_credentials)

        # --- Sorting and deduplicating --- #
        sort_task = progress.add_task("[magenta]Sorting and deduplicating...", total=total_credentials)

        start_time = time.time()
        unique_credentials = []
        seen = set()
        for i, cred in enumerate(sorted(all_credentials, key=lambda x: x[0].lower())):
            email, password = cred
            if email.lower() not in seen:
                seen.add(email.lower())
                unique_credentials.append((email, password))            
            progress.update(sort_task, advance=1)
        progress.update(sort_task, completed=total_credentials)

        # --- Writing output --- #
        output_dir = output_path / f"{input_path.name}___output"
        input_name = input_path.name  # Just the name of the subdirectory (e.g. creddump/folder1 -> folder1)
        write_task = progress.add_task("[magenta]Writing output...", total=len(unique_credentials))
        await write_output(output_dir, input_name, unique_credentials, split_size, progress, write_task)

    return {
        "total_files": len(results),
        "total_credentials": len(all_credentials),
        "unique_credentials": len(unique_credentials),
        "failed_files": failed_files,
        "results": results
    }
