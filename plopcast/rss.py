from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
from pydantic import BaseModel


def require_el(element: ET.Element | None):
    if element is None:
        raise RuntimeError("Required element not found!")
    return element


def require_str(s: str | None):
    if s is None:
        raise RuntimeError("Required string not found!")
    return s


class RSSItem(BaseModel):
    title: str
    link: str
    description: str
    enclosure: str
    itunes_image: str
    pub_date: datetime

    @classmethod
    def from_xml(cls, root: ET.Element, namespaces: dict[str, str]) -> RSSItem:
        image_tag = root.find("itunes:image", namespaces)

        return cls(
            title=require_str(root.findtext("title")),
            link=root.findtext("link") or "",
            description=require_str(root.findtext("description")),
            enclosure=require_str(require_el(root.find("enclosure")).get("url")),
            itunes_image=require_str(image_tag.get("href"))
            if image_tag is not None
            else "",
            pub_date=parsedate_to_datetime(require_str(root.findtext("pubDate"))),
        )


class RSSFeed(BaseModel):
    title: str
    link: str
    description: str
    items: list[RSSItem]

    @classmethod
    def from_xml(cls, root: ET.Element, namespaces: dict[str, str]) -> RSSFeed:
        channel = root.find("channel")
        if channel is None:
            raise ValueError("Invalid RSS feed: no channel element found")

        return RSSFeed(
            title=channel.findtext("title", ""),
            link=channel.findtext("link", ""),
            description=channel.findtext("description", ""),
            items=[
                RSSItem.from_xml(item_content, namespaces)
                for item_content in channel.findall("item")
            ],
        )


def _parse_rss_xml(xml_content: str) -> RSSFeed:
    """Parse RSS XML content into an RSSFeed instance."""

    # Extract namespaces from the XML
    namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

    root = ET.fromstring(xml_content)
    return RSSFeed.from_xml(root, namespaces)


def get_rss_feed(url: str) -> RSSFeed:
    response = requests.get(url, headers={"User-Agent": "Plopcast RSS Reader"})
    if response.status_code == 200:
        return _parse_rss_xml(response.text)
    else:
        raise Exception(
            f"Failed to download RSS feed: {response.status_code} {response.content}"
        )
