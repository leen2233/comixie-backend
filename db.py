import os
from dataclasses import asdict, dataclass
from typing import List, Optional

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(
    host=os.getenv("MONGO_HOST"),
    port=int(os.getenv("MONGO_PORT", "27017"))
)
db = client.comixie

@dataclass
class Comic:
    slug: str
    url: str
    _id: Optional[str|ObjectId] = None
    genres: Optional[List[str]] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


@dataclass
class Chapter:
    slug: str
    comic_slug: str
    name: str
    url: str
    _id: Optional[str|ObjectId] = None
    images: Optional[List] = None


class ComicManager:
    def __init__(self):
        pass

    def get(self, slug: str) -> Optional[Comic]:
        item = db.comics.find_one({"slug": slug})
        if item:
            item = Comic(**item)
            item._id = str(item._id)
            return item
        return None

    def create(self, comic: Comic):
        data = asdict(comic)
        data.pop("_id")
        item = db.comics.insert_one(data)
        return item


class ChapterManager:
    def __init__(self):
        pass

    def get(self, slug: str) -> Optional[Chapter]:
        item = db.chapters.find_one({"slug": slug})
        if item:
            item = Chapter(**item)
            item._id = str(item._id)
            return item
        return None

    def create(self, chapter: Chapter):
        data = asdict(chapter)
        data.pop("_id")
        item = db.chapters.insert_one(data)
        return item

    def update(self, slug: str, images: list):
        db.chapters.update_one({'slug': slug}, {'$set': {'images': images}})
        return True

comics = ComicManager()
chapters = ChapterManager()
genres = db.genres
