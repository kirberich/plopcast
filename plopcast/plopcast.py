"""Download podcast media and deal with filenames and other metadata"""

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from mutagen.easyid3 import EasyID3

from plopcast.rss import RSSFeed, RSSItem

# As people often save podcasts on fat32 file systems, we sanitise all filenames to not contain characters
# which are invalid in fat32
INVALID_CHARACTERS = r'\<|\>|\:|"|\/|\|\|\?\*'

EpisodeCheck = tuple[RSSItem, bool, Path, str]


@dataclass(kw_only=True, slots=True)
class Plopcast:
    feed: RSSFeed
    output_path: Path
    max_episodes: int | None
    album_tag: str | None
    artist_tag: str | None
    overwrite: bool
    retag: bool
    file_prefix_template: str
    set_modification_time: bool

    def _episode_filename(self, item: RSSItem):
        file_url = urlparse(item.enclosure)
        original_filename = file_url.path.rsplit("/", 1)[-1]
        _, file_suffix = original_filename.rsplit(".", 1)

        prefix = self.file_prefix_template.format(
            title=item.title,
            date=item.pub_date,
            original_prefix=original_filename.rsplit(".", 1)[0],
        )

        sanitised_prefix = re.sub(INVALID_CHARACTERS, "", prefix)
        return f"{sanitised_prefix}.{file_suffix}"

    # def _tag_mp3(self, item: RSSItem, metadata: eyed3.AudioFile):
    #     if metadata.tag is None:  # type: ignore
    #         metadata.tag = Tag()
    #     if self.album_tag:
    #         metadata.tag.album = self.album_tag
    #     if self.artist_tag:
    #         metadata.tag.artist = self.artist_tag

    #     if not metadata.tag.title:  # type: ignore
    #         # Set a title if it's missing
    #         metadata.tag.title = item.title

    #     metadata.tag.save()  # type: ignore

    def _tag_mp3(self, item: RSSItem, output_file: Path):
        metadata = EasyID3(output_file)
        if not metadata.get("title"):
            metadata["title"] = item.title
        if self.album_tag:
            metadata["album"] = self.album_tag
        if self.artist_tag:
            metadata["artist"] = self.album_tag

        metadata.save()  # type: ignore

    def tag_file(self, item: RSSItem, output_file: Path):
        """Set metadata tags and file attributes in the output file.

        FIXME: currently only supports mp3
        """
        if output_file.suffix.lower() == ".mp3":
            self._tag_mp3(item, output_file)

        if self.set_modification_time:
            mod_time = item.pub_date.timestamp()
            os.utime(output_file, (mod_time, mod_time))

    def download_episode(self, item: RSSItem, output_file: Path):
        print(f"Downloading {item.enclosure}...")

        response = requests.get(
            item.enclosure, headers={"User-Agent": "Plopcast RSS Reader"}
        )
        response.raise_for_status()
        data = response.content

        print(f"Saving as {output_file}...")
        with open(output_file, "wb") as f:
            f.write(data)

        # Fix any missing metadata
        self.tag_file(item, output_file)

    def check_episodes(self) -> Iterable[EpisodeCheck]:
        for index, item in enumerate(self.feed.items):
            filename = self._episode_filename(item)
            output_file = self.output_path / filename

            if self.max_episodes is not None and index >= self.max_episodes:
                yield item, False, output_file, f"Max {self.max_episodes} episodes"
                continue

            match output_file.exists(), self.overwrite:
                case False, _:
                    yield item, True, output_file, "New"
                case True, True:
                    yield item, True, output_file, "Overwrite"
                case True, False:
                    yield item, False, output_file, "Exists"

    def download_episodes(self):
        """Download episodes, according to the given options."""

        for item, should_download, output_file, _ in self.check_episodes():
            if should_download:
                self.download_episode(item, output_file)
            if should_download or self.retag and output_file.exists():
                self.tag_file(item, output_file)
