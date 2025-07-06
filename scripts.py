import pprint
import re
from enum import Enum
from typing import Dict

import cloudscraper
from bs4 import BeautifulSoup as BS


class Status(Enum):
    """
    Enum for the different steps
    """

    DOWNLOADING = "Downloading"
    CROPPING = "Cropping"
    ADDING_PAGES = "Adding Pages"
    EXPORTING = "Exporting PDF"
    COMPLETE = "Complete!"


def get_status_length() -> int:
    """
    returns length of the longest Status string
    """
    res = 0
    for status in Status:
        res = max(res, len(status.value))
    return res

scraper = cloudscraper.create_scraper()


__author__ = "nighmared"
__version__ = 1.21


DEBUG = False  # makes it more verbose
PDF_H = 300  # Height of resulting PDF
PDF_W = 200  # Width of resulting PDF
# For most comics i have seen an aspect ratio of 2:3 seems to be a good call

PROGRESS_BAR_LEN = 50  # lenght of the progress bar that is displayed
STATUS_LEN = (
    get_status_length() + 1
)  # How much space must be accounted for the status in the progress bar
NUM_STEPS = len(Status)  # Number of steps the program goes through
STEP_SIZE = PROGRESS_BAR_LEN // NUM_STEPS  # equal length parts for the status bar


def get_comic_images(entry: dict) -> dict:
    url = entry.get("url", "").strip()
    name = entry.get("name", "").strip()
    base = scraper.get(url)
    base.close()
    soup = BS(base.content, "html.parser")
    pages = soup.select("center p img")
    urls = []

    for page in pages:
        source = page["src"]
        if isinstance(source, list):
            raise AttributeError("Image can't have more than one source")
        urls.append(source)

    return {"name": name, "urls": urls}


def search_comics(query: str):
    """
    Search for comics on readallcomics.com

    Args:
        query (str): Search term for comics
        nonce (str): Security nonce (default provided)

    Returns:
        Dict containing search results with title and URL for each comic
    """

    # URL and headers
    url = f"https://readallcomics.com/?story={query}&s=&type=comic"

    try:
        # Make the request
        response = scraper.post(url, timeout=10)
        response.raise_for_status()

        # Parse the HTML response
        html_content = response.text.strip('"').replace("\\", "")  # Remove surrounding quotes
        # Extract links and titles using regex
        link_pattern = r'<a href="([^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(link_pattern, html_content)
        # Process results
        results = []
        for url, title in matches:
            # Clean up the URL (unescape HTML entities)
            clean_title = title.strip()
            if "/category" in url:
                results.append({
                    'title': clean_title,
                    'url': url
                })

        return {
            'query': query,
            'total_results': len(results),
            'results': results
        }

    except Exception as e:
        return {
            'query': query,
            'error': f'Parsing failed: {str(e)}',
            'total_results': 0,
            'results': []
        }

def print_results(results: Dict) -> None:
    """Pretty print the search results"""
    print(f"\nSearch Query: '{results['query']}'")
    print(f"Total Results: {results['total_results']}")

    if 'error' in results:
        print(f"Error: {results['error']}")
        return

    print("\nResults:")
    print("-" * 80)

    for i, result in enumerate(results['results'], 1):
        print(f"{i:2d}. {result['title']}")
        print(f"    URL: {result['url']}")
        print()

def get_comic_details(url):
    response = scraper.get(url)
    soup = BS(response.content, "html.parser")

    chapters = []
    genres_element = publisher_element = title = genres = publisher = description = image = None

    title_element = soup.select_one("center div h1 b")
    image_element = soup.select_one("center p img")
    description_element = str(soup.select_one("div.b"))

    info = soup.select_one("center div div p")
    chapters_element = soup.find(attrs={"class": "list-story"})

    if chapters_element:
        links = chapters_element.find_all("a")
        for link in links:
            name = link.get_text(strip=True)
            url = link["href"]
            chapters.append({"url": url, "name": name})

    if info:
        genres_element = info.find_next("strong")
        if genres_element:
            publisher_element = genres_element.find_next("strong")

    if title_element:
        title = title_element.text
    if genres_element:
        genres = genres_element.text.split(", ")
    if publisher_element:
        publisher = publisher_element.text
    if image_element:
        image = image_element.get("src")

    match = re.search(r'</span><br/>(.*?)<br/>', description_element, re.DOTALL)
    if match:
        description = match.group(1).strip()

    return {
        "title": title,
        "genres": genres,
        "publisher": publisher,
        "desccription": description,
        "chapters": chapters,
        "image": image
    }


def home_page(page=1):
    url = f"https://readallcomics.com/page/{page}/"
    response = scraper.get(url)
    soup = BS(response.content, "html.parser")

    divs = soup.find_all('div', {'id': lambda x: x and x.startswith('post-'), 'class': lambda x: x and 'post-' in x}) # type: ignore
    for div in divs:
        url = div.select_one("a").get("href")
        image = div.select_one("img").get("src")
        name = div.find("a", attrs={"class": "front-link"})
        date = div.select_one("center span").text
        print(url, image, name.text, date)

def get_page_count():
    url = "https://readallcomics.com/"
    response = scraper.get(url)
    soup = BS(response.content, "html.parser")

    numbers = soup.find_all('a', {"class": "page-numbers"}) # type: ignore
    for div in divs:
        url = div.select_one("a").get("href")
        image = div.select_one("img").get("src")
        name = div.find("a", attrs={"class": "front-link"})
        date = div.select_one("center span").text
        print(url, image, name.text, date)


def get_comic_page(url):
    response = scraper.get(url)
    html_content = response.text.strip('"').replace("\\", "")

    link_pattern = r'<a href="(https://readallcomics\.com/category/[\w-]+/)"[^>]*>([^<]*)</a>'
    matches = re.findall(link_pattern, html_content)
    print(matches)


# Example usage
if __name__ == "__main__":
    # Search for Spider-Man comics
    # search_query = input("Enter comic search query (or press Enter for 'the amazing spider-man'): ").strip()
    # if not search_query:
    #     search_query = "the amazing spider-man"

    # print(f"Searching for: {search_query}")
    # results = search_comics(search_query)
    ## result url example: https://readallcomics.com/category/the-amazing-spider-man-the-origin-of-the-hobgoblin/  . you will give only slug

    # Print results
    # print_results(results)
    # index = int(input("Enter number of which result: "))

    # details = get_comic_details(results["results"][index - 1].get("url"))
    # get_comic_page("https://readallcomics.com/rick-and-morty-ricklemania-004-2025/")
    details = get_comic_details("https://readallcomics.com/category/nacelleverse-biker-mice-from-mars-and-roboforce/")
    pprint.pprint(details)
    ## chapter url example: https://readallcomics.com/the-amazing-spider-man-the-movie-adaptation-1/ you will get only slug

    # which_chapter = int(input("Enter which chapter to download: "))

    # urls = get_comic_images(details.get("chapters", [])[which_chapter - 1])
    # home_page(page=2)
