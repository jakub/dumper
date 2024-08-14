import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from dumper.processor import process_files
from dumper.ui import create_file_console, display_header, display_results


def parse_arguments(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dumper - Credential parsing and normalization tool")
    parser.add_argument("input_path", type=Path, help="Input directory or file path")
    parser.add_argument("-o", "--output", type=Path, default=Path.cwd(), help="Output directory path (default: current working directory)")
    parser.add_argument("-e", "--ext", type=str, help="File extensions to process (default: all files)")
    parser.add_argument("-s", "--split", type=int, help="Split output into files with specified number of lines")
    parser.add_argument("-n", "--no-ui", action="store_true", help="Disable rich UI and output to report.txt")
    
    return parser.parse_args(args)


async def async_main(args: Optional[List[str]] = None) -> None:
    if args is None:
        args = sys.argv[1:]

    parsed_args = parse_arguments(args)
    
    output_dir = parsed_args.output / f"{parsed_args.input_path.name}___output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if parsed_args.no_ui:
        console = create_file_console(output_dir / "report.txt")
    else:
        console = Console()

    display_header(console, parsed_args)
    results = await process_files(parsed_args, console)
    display_results(console, results)

    if parsed_args.no_ui:
        console.file.close()


def main(args: Optional[List[str]] = None) -> None:
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
