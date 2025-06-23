# Comixie Backend

A powerful Flask-based backend service for the Comixie comic reading platform, providing a robust API for comic discovery, chapter reading, and PDF export functionality.

## 🚀 Current Features

### Comic Discovery

- **Comic Search**
  - Full-text search across comic titles
  - Integration with ReadAllComics.com for comprehensive comic data
  - Real-time search results with title, URL, and slug information
  - Error handling for failed searches

- **Comic Details**
  - Detailed comic information including title, genres, and publisher
  - Comic descriptions and cover images
  - Complete chapter listings with individual chapter URLs
  - Metadata extraction from comic pages

### Chapter Reading

- **Chapter Content**
  - Full chapter image extraction
  - Sequential page ordering
  - High-quality image URL retrieval
  - Support for variable page counts per chapter

- **Image Processing**
  - Automatic image fetching and processing
  - Error handling for missing or corrupted images
  - Optimized image delivery

### PDF Export

- **PDF Generation**
  - Convert entire chapters to PDF format
  - Automatic image resizing and aspect ratio preservation
  - Optimized PDF layout (200x300 page size)
  - Professional PDF formatting with proper page breaks

- **Download Features**
  - Direct PDF download functionality
  - Custom filename generation based on chapter slug
  - Streaming PDF delivery for large files

### Content Aggregation

- **Home Page Feed**
  - Latest comics discovery
  - Paginated comic listings
  - Comic metadata including publication dates
  - Thumbnail image support

### Technical Features

- **Web Scraping**
  - CloudScraper integration for anti-bot protection
  - BeautifulSoup HTML parsing
  - Robust error handling and timeout management
  - Regular expression pattern matching

## 🛠️ Technical Stack

- **Framework**: Flask with CORS support
- **Web Scraping**: CloudScraper + BeautifulSoup4
- **Image Processing**: Pillow (PIL)
- **PDF Generation**: ReportLab
- **HTTP Client**: CloudScraper (anti-detection)
- **HTML Parsing**: BeautifulSoup4
- **Pattern Matching**: Python regex

## 🚀 Getting Started

1. **Prerequisites**
   - Python 3.8+
   - pip
   - virtualenv (recommended)

2. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install flask flask-cors cloudscraper beautifulsoup4 pillow reportlab
   ```

3. **Running the Server**
   ```bash
   python main.py
   ```
   The server will start on `http://localhost:5000`

4. **Testing the API**
   ```bash
   # Search for comics
   curl "http://localhost:5000/api/search?q=batman"

   # Get comic details
   curl "http://localhost:5000/api/details/batman-dark-knight"

   # Health check
   curl "http://localhost:5000/api/health"
   ```

## 🔧 Configuration

### PDF Settings
- **Page Size**: 200x300 pixels (optimized for mobile reading)
- **Image Scaling**: Automatic aspect ratio preservation
- **Timeout**: 30 seconds per image download

### Scraping Settings
- **CloudScraper**: Anti-detection web scraping
- **Timeout**: 10 seconds for search requests
- **User Agent**: Rotating user agents for better success rates

## 🎯 Planned Features

### Enhanced Reading Experience
- **Reading Progress Tracking**
  - Bookmark system
  - Reading history
  - Progress synchronization

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This project is for educational purposes only. Please respect the terms of service of the websites being scraped and ensure compliance with applicable laws and regulations.

## 🙏 Acknowledgments

- ReadAllComics.com for comic content
- Flask community for the excellent web framework
- CloudScraper developers for anti-detection capabilities
- ReportLab team for PDF generation tools
- BeautifulSoup contributors for HTML parsing
