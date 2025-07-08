import sqlite3

import cloudscraper
from bs4 import BeautifulSoup as BS

scraper = cloudscraper.create_scraper()

# Connect DB and ensure tables exist
conn = sqlite3.connect('comics.db')
c = conn.cursor()

c.execute("SELECT id, slug, url FROM comics")
comics = c.fetchall()

def get_comic_image(url):
    response = scraper.get(url)
    soup = BS(response.content, "html.parser")

    image = None
    image_element = soup.select_one("center p img")
    if image_element:
        image = image_element.get("src")

    return image

count = 0
for comic_id, slug, url in comics:
    try:
        image = get_comic_image(url)
        if image:
            c.execute("UPDATE comics SET image = ? WHERE id = ?", (image, comic_id))
            count += 1
            if count % 50 == 0:
                print(f"[SUCCESS] Processed {count} chapters...")
                conn.commit()
        else:
            print("[COULDNT GET IMAGE]", url)
    except Exception as e:
        print(f"Error on chapter {chap_id}: {e}")

conn.commit()
conn.close()
print("Scraping complete. Data stored in comics.db")
