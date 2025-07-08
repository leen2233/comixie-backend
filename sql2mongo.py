import os
import sqlite3
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH")
if not DATABASE_PATH:
    raise Exception("Please set DATABASE_PATH at .env to run this script")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

client = MongoClient(
    host=os.getenv("MONGO_HOST"),
    port=int(os.getenv("MONGO_PORT", "27017"))
)
db = client.comixie

cursor.execute("SELECT * FROM genres")

for id, name in cursor.fetchall():
    db.genres.insert_one({'name': name})


# comics

cursor.execute("SELECT id, name FROM genres")
genre_map = dict(cursor.fetchall())

cursor.execute("SELECT comic_id, genre_id FROM comic_genres")
comic_genres = {}
for comic_id, genre_id in cursor.fetchall():
    comic_genres.setdefault(comic_id, []).append(genre_map[genre_id])

cursor.execute("SELECT id, slug, title, url, description, publisher, image FROM comics")
docs = []
for row in cursor.fetchall():
    comic_id, *data = row

    doc = dict(zip(['id', 'slug', 'title', 'url', 'description', 'publisher', 'image'], row))
    doc['genres'] = comic_genres.get(comic_id, [])
    doc.pop('id')
    docs.append(doc)

# Insert in batches
batch_size = 1000
for i in range(0, len(docs), batch_size):
    db.comics.insert_many(docs[i:i + batch_size])


# chapters
def batch_generator(cursor, size=1000):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        yield rows


cursor.execute("SELECT id, slug FROM comics")
comic_slug_map = dict(cursor.fetchall())
cursor.execute("SELECT id, comic_id, slug, name, url FROM chapters")
for rows in batch_generator(cursor):
    docs = []
    for row in rows:
        chap_id, comic_id, slug, name, url = row
        docs.append({
            "comic_slug": comic_slug_map.get(comic_id),
            "slug": slug,
            "name": name,
            "url": url
        })
    db.chapters.insert_many(docs)
