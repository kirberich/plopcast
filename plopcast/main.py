from pathlib import Path
from typing import Annotated

import typer
from rich import print

from plopcast.plopcast import Plopcast

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
    album_tag: Annotated[
        str | None, typer.Option(help="Album name to set in file metadata")
    ] = None,
    artist_tag: Annotated[
        str | None, typer.Option(help="Artist name to set in file metadata")
    ] = None,
    overwrite: Annotated[
        bool, typer.Option(help="Redownload and overwrite existing episodes")
    ] = False,
    retag: Annotated[
        bool,
        typer.Option(
            help="Reapply metadata tags and file attributes, even if file is already downloaded"
        ),
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

    plopcast = Plopcast(
        feed=feed,
        output_path=output_dir,
        max_episodes=max_episodes,
        album_tag=album_tag,
        artist_tag=artist_tag,
        overwrite=overwrite,
        retag=retag,
        file_prefix_template=file_prefix_template,
        set_modification_time=set_modification_time,
    )

    if not quiet:
        for item, should_download, output_file, reason in plopcast.check_episodes():
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

    plopcast.download_episodes()


def cli():
    typer.run(main)
