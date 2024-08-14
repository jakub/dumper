import asyncio
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import humanize
from rich.progress import Progress, TaskID


async def write_output(output_dir: Path, input_name: str, credentials: List[Tuple[str, str]], split_size: int = None, progress: Progress = None, task_id: TaskID = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_filename = f"{input_name}___{timestamp}_{humanize.metric(len(credentials))}".replace(" ", "")
    
    total_credentials = len(credentials)
    credentials_written = 0

    if split_size:
        for i, chunk in enumerate(split_list(credentials, split_size), 1):
            filename = f"{base_filename}_{i}.csv"
            await write_csv(output_dir / filename, chunk)
            credentials_written += len(chunk)
            if progress and task_id:
                progress.update(task_id, completed=credentials_written)
    else:
        filename = f"{base_filename}.csv"
        await write_csv(output_dir / filename, credentials)
        if progress and task_id:
            progress.update(task_id, completed=total_credentials)

async def write_csv(file_path: Path, data: List[Tuple[str, str]]) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, write_csv_sync, file_path, data)

def write_csv_sync(file_path: Path, data: List[Tuple[str, str]]) -> None:
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['email', 'password'])
        writer.writerows(data)

def split_list(lst: List, n: int) -> List[List]:
    return [lst[i:i + n] for i in range(0, len(lst), n)]
