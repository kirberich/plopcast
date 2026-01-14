"""Download podcast media and deal with filenames and other metadata"""

import os
import re
from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlparse

import requests

from plopcast.rss import RSSFeed, RSSItem

# As people often save podcasts on fat32 file systems, we sanitise all filenames to not contain characters
# which are invalid in fat32
INVALID_CHARACTERS = r'\<|\>|\:|"|\/|\|\|\?\*'

EpisodeCheck = tuple[RSSItem, bool, Path, str]


def episode_filename(item: RSSItem, filename_template: str):
    file_url = urlparse(item.enclosure)
    original_filename = file_url.path.rsplit("/", 1)[-1]
    _, file_suffix = original_filename.rsplit(".", 1)

    prefix = filename_template.format(
        title=item.title,
        date=item.pub_date,
        original_prefix=original_filename.rsplit(".", 1)[0],
    )

    sanitised_prefix = re.sub(INVALID_CHARACTERS, "", prefix)
    return f"{sanitised_prefix}.{file_suffix}"


def download_episode(item: RSSItem, output_file: Path, set_modification_time: bool):
    print(f"Downloading {item.enclosure}...")

    response = requests.get(
        item.enclosure, headers={"User-Agent": "Plopcast RSS Reader"}
    )
    response.raise_for_status()
    data = response.content

    print(f"Saving as {output_file}...")
    with open(output_file, "wb") as f:
        f.write(data)

    if set_modification_time:
        mod_time = item.pub_date.timestamp()
        os.utime(output_file, (mod_time, mod_time))


def check_episodes(
    feed: RSSFeed,
    output_path: Path,
    max_episodes: int | None,
    overwrite: bool,
    file_prefix_template: str,
) -> Iterable[EpisodeCheck]:
    for index, item in enumerate(feed.items):
        filename = episode_filename(item, file_prefix_template)
        output_file = output_path / filename

        if max_episodes is not None and index > max_episodes:
            yield item, False, output_file, f"Max {max_episodes} episodes"
            continue

        match output_file.exists(), overwrite:
            case False, _:
                yield item, True, output_file, "New"
            case True, True:
                yield item, True, output_file, "Overwrite"
            case True, False:
                yield item, False, output_file, "Exists"


def download_episodes(
    feed: RSSFeed,
    output_path: Path,
    max_episodes: int | None,
    overwrite: bool,
    file_prefix_template: str,
    set_modification_time: bool,
):
    """Download episodes, according to the given options."""

    for item, should_download, output_file, _ in check_episodes(
        feed, output_path, max_episodes, overwrite, file_prefix_template
    ):
        if not should_download:
            continue

        download_episode(item, output_file, set_modification_time)
