from pathlib import Path
from typing import Annotated

import typer
from rich import print

from .media import check_episodes, download_episodes
from .rss import get_rss_feed


def main(
    url: Annotated[str, typer.Option(help="RSS feed URL")],
    output_dir: Annotated[Path, typer.Option(help="Path for saved episodes")],
    max_episodes: Annotated[
        int | None,
        typer.Option(
            help="Maximum number of most recent episodes to fetch (Default is all episodes)"
        ),
    ] = None,
    overwrite: Annotated[
        bool, typer.Option(help="Redownload and overwrite existing episodes")
    ] = False,
    file_prefix_template: Annotated[
        str,
        typer.Option(
            help="Template for the filename prefix. Available variables are {title}, {date} and {original_prefix}"
        ),
    ] = "{date:%Y-%m-%d} {title}",
    set_modification_time: Annotated[
        bool,
        typer.Option(
            help="Set modification time of created file to the publication date of the episode"
        ),
    ] = True,
    quiet: Annotated[
        bool,
        typer.Option(
            help="Don't show any details about which episodes will be downloaded"
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option(help="Show extra details about skipped episodes")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option(help="Don't actually download anything")
    ] = False,
):
    feed = get_rss_feed(url)

    if not quiet:
        for item, should_download, output_file, reason in check_episodes(
            feed, output_dir, max_episodes, overwrite, file_prefix_template
        ):
            if should_download:
                print(
                    f"[green]{reason.ljust(20)}[bold]{item.title}[/bold][/green] [bright_black]({output_file})[/bright_black]"
                )
            elif verbose:
                print(f"[yellow]{reason.ljust(20)}Skipping {item.title}[/yellow]")

    if dry_run:
        return

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    download_episodes(
        feed,
        output_path=output_dir,
        max_episodes=max_episodes,
        overwrite=overwrite,
        file_prefix_template=file_prefix_template,
        set_modification_time=set_modification_time,
    )


def cli():
    typer.run(main)
