import io
import re
from enum import Enum

import cloudscraper
from bs4 import BeautifulSoup as BS
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

app = Flask(__name__)
CORS(app)

scraper = cloudscraper.create_scraper()

class Status(Enum):
    DOWNLOADING = "Downloading"
    CROPPING = "Cropping"
    ADDING_PAGES = "Adding Pages"
    EXPORTING = "Exporting PDF"
    COMPLETE = "Complete!"

PDF_H = 300
PDF_W = 200


@app.route('/api/search', methods=['GET'])
def search_comics():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    url = f"https://readallcomics.com/?story={query}&s=&type=comic"

    try:
        response = scraper.post(url, timeout=10)
        print(response.status_code, response.text)
        response.raise_for_status()

        html_content = response.text.strip('"').replace("\\", "")
        link_pattern = r'<a href="([^"]*)"[^>]*>([^<]*)</a>'
        matches = re.findall(link_pattern, html_content)

        results = []
        for url, title in matches:
            clean_title = title.strip()
            if "/category" in url:
                results.append({
                    'title': clean_title,
                    'url': url,
                    'slug': url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
                })

        return jsonify({
            'query': query,
            'total_results': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({
            'query': query,
            'error': f'Search failed: {str(e)}',
            'total_results': 0,
            'results': []
        }), 500

@app.route('/api/details/<path:slug>', methods=['GET'])
def get_comic_details(slug):
    url = f"https://readallcomics.com/category/{slug}/"

    try:
        response = scraper.get(url)
        if response.status_code != 200:
            return jsonify({"error": "comic not found"}), response.status_code
        soup = BS(response.content, "html.parser")

        chapters = []
        title = genres = publisher = description = image = None

        title_element = soup.select_one("center div h1 b")
        description_element = str(soup.select_one("div.b"))
        image_element = soup.select_one("center p img")
        info = soup.select_one("center div div p")
        chapters_element = soup.find(attrs={"class": "list-story"})

        if chapters_element:
            links = chapters_element.find_all("a") # type: ignore
            for link in links:
                name = link.get_text(strip=True)
                chapter_url = link["href"] # type: ignore
                chapter_slug = chapter_url.split('/')[-2] if chapter_url.endswith('/') else chapter_url.split('/')[-1] # type: ignore
                chapters.append({
                    "url": chapter_url,
                    "name": name,
                    "slug": chapter_slug
                })

        if info:
            genres_element = info.find_next("strong")
            if genres_element:
                publisher_element = genres_element.find_next("strong")
                if genres_element:
                    genres = genres_element.text.split(", ")
                if publisher_element:
                    publisher = publisher_element.text

        if title_element:
            title = title_element.text

        if image_element:
            image = image_element.get("src")

        match = re.search(r'</span><br/>(.*?)<br/>', description_element, re.DOTALL)
        if match:
            description = match.group(1).strip()

        return jsonify({
            "title": title,
            "genres": genres,
            "publisher": publisher,
            "description": description,
            "chapters": chapters,
            "image": image
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get details: {str(e)}'}), 500

@app.route('/api/read/<path:chapter_slug>', methods=['GET'])
def read_chapter(chapter_slug):
    chapter_url = f"https://readallcomics.com/{chapter_slug}/"

    try:
        base = scraper.get(chapter_url)
        soup = BS(base.content, "html.parser")
        pages = soup.select("center p img")

        urls = []
        for page in pages:
            source = page["src"]
            if isinstance(source, list):
                raise AttributeError("Image can't have more than one source")
            urls.append(source)

        return jsonify({
            "chapter_slug": chapter_slug,
            "chapter_url": chapter_url,
            "total_pages": len(urls),
            "image_urls": urls
        })

    except Exception as e:
        return jsonify({'error': f'Failed to read chapter: {str(e)}'}), 500

@app.route('/api/export-pdf/<path:chapter_slug>', methods=['POST'])
def export_pdf(chapter_slug):
    try:
        chapter_data = read_chapter(chapter_slug)
        if isinstance(chapter_data, tuple):
            return chapter_data

        chapter_info = chapter_data.get_json()
        image_urls = chapter_info['image_urls']

        if not image_urls:
            return jsonify({'error': 'No images found'}), 400

        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=(PDF_W, PDF_H))

        for i, img_url in enumerate(image_urls):
            try:
                img_response = scraper.get(img_url, timeout=30)
                img_response.raise_for_status()

                img = Image.open(io.BytesIO(img_response.content))
                img_width, img_height = img.size

                aspect_ratio = img_width / img_height
                if aspect_ratio > PDF_W / PDF_H:
                    new_width = PDF_W
                    new_height = PDF_W / aspect_ratio
                else:
                    new_height = PDF_H
                    new_width = PDF_H * aspect_ratio

                x_offset = (PDF_W - new_width) / 2
                y_offset = (PDF_H - new_height) / 2

                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)

                img_reader = ImageReader(img_buffer)
                pdf_canvas.drawImage(img_reader, x_offset, y_offset,
                                   width=new_width, height=new_height)

                if i < len(image_urls) - 1:
                    pdf_canvas.showPage()

            except Exception:
                continue

        pdf_canvas.save()
        pdf_buffer.seek(0)

        filename = f"{chapter_slug}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

@app.route('/api/home', methods=['GET'])
def home_page():
    page = request.args.get('page', 1, type=int)
    url = f"https://readallcomics.com/page/{page}/"

    try:
        response = scraper.get(url)
        soup = BS(response.content, "html.parser")
        divs = soup.find_all('div', {'id': lambda x: x and x.startswith('post-'), 'class': lambda x: x and 'post-' in x}) # type: ignore

        comics = []
        for div in divs:
            try:
                comic_url = div.select_one("a").get("href") # type: ignore
                image = div.select_one("img").get("src") # type: ignore
                name_element = div.find("a", attrs={"class": "front-link"}) # type: ignore
                date = div.select_one("center span").text # type: ignore

                slug = comic_url.split('/')[-2] if comic_url.endswith('/') else comic_url.split('/')[-1] # type: ignore

                comics.append({
                    'url': comic_url,
                    'slug': slug,
                    'image': image,
                    'name': name_element.text if name_element else '',
                    'date': date
                })
            except Exception:
                continue

        return jsonify({
            'page': page,
            'total_comics': len(comics),
            'comics': comics
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get home page: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Comic API is running'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
