import os
import sys
import time
import unittest

import requests

# Assuming the Flask app is in the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class ComicAPITestCase(unittest.TestCase):
    BASE_URL = "http://localhost:5000/api"

    @classmethod
    def setUpClass(cls):
        print("Starting tests - Make sure Flask server is running on localhost:5000")
        time.sleep(1)

    def test_01_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('message', data)
        print("✓ Health check passed")

    def test_02_home_page_default(self):
        """Test home page with default page"""
        response = requests.get(f"{self.BASE_URL}/home")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('page', data)
        self.assertIn('total_comics', data)
        self.assertIn('comics', data)
        self.assertEqual(data['page'], 1)
        self.assertIsInstance(data['comics'], list)

        if data['comics']:
            comic = data['comics'][0]
            required_fields = ['url', 'slug', 'image', 'name', 'date']
            for field in required_fields:
                self.assertIn(field, comic)

        print(f"✓ Home page default - Found {data['total_comics']} comics")

    def test_03_home_page_with_page_number(self):
        """Test home page with specific page number"""
        response = requests.get(f"{self.BASE_URL}/home?page=2")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['page'], 2)
        self.assertIn('comics', data)
        print(f"✓ Home page 2 - Found {data['total_comics']} comics")

    def test_04_search_comics(self):
        """Test comic search functionality"""
        search_query = "spider"
        response = requests.get(f"{self.BASE_URL}/search?q={search_query}")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('query', data)
        self.assertIn('total_results', data)
        self.assertIn('results', data)
        self.assertEqual(data['query'], search_query)
        self.assertIsInstance(data['results'], list)

        if data['results']:
            result = data['results'][0]
            required_fields = ['title', 'url', 'slug']
            for field in required_fields:
                self.assertIn(field, result)

        print(f"✓ Search '{search_query}' - Found {data['total_results']} results")

        # Store first result for next test
        if data['results']:
            self.test_slug = data['results'][0]['slug']

    def test_05_search_empty_query(self):
        """Test search with empty query"""
        response = requests.get(f"{self.BASE_URL}/search")
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertIn('error', data)
        print("✓ Empty search query properly rejected")

    def test_06_get_comic_details(self):
        """Test getting comic details"""
        # Use a known slug or get from search
        if not hasattr(self, 'test_slug'):
            search_response = requests.get(f"{self.BASE_URL}/search?q=batman")
            search_data = search_response.json()
            if search_data['results']:
                self.test_slug = search_data['results'][0]['slug']
            else:
                self.skipTest("No search results available for testing details")

        response = requests.get(f"{self.BASE_URL}/details/{self.test_slug}")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        expected_fields = ['title', 'genres', 'publisher', 'description', 'chapters']
        for field in expected_fields:
            self.assertIn(field, data)

        self.assertIsInstance(data['chapters'], list)

        if data['chapters']:
            chapter = data['chapters'][0]
            chapter_fields = ['url', 'name', 'slug']
            for field in chapter_fields:
                self.assertIn(field, chapter)
            # Store chapter slug for next test
            self.test_chapter_slug = chapter['slug']

        print(f"✓ Comic details for '{self.test_slug}' - Found {len(data['chapters'])} chapters")

    def test_07_read_chapter(self):
        """Test reading a chapter"""
        if not hasattr(self, 'test_chapter_slug'):
            # Get a chapter slug from comic details
            if not hasattr(self, 'test_slug'):
                search_response = requests.get(f"{self.BASE_URL}/search?q=batman")
                search_data = search_response.json()
                if search_data['results']:
                    self.test_slug = search_data['results'][0]['slug']
                else:
                    self.skipTest("No search results available")

            details_response = requests.get(f"{self.BASE_URL}/details/{self.test_slug}")
            details_data = details_response.json()
            if details_data['chapters']:
                self.test_chapter_slug = details_data['chapters'][0]['slug']
            else:
                self.skipTest("No chapters available for testing")

        response = requests.get(f"{self.BASE_URL}/read/{self.test_chapter_slug}")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        expected_fields = ['chapter_slug', 'chapter_url', 'total_pages', 'image_urls']
        for field in expected_fields:
            self.assertIn(field, data)

        self.assertEqual(data['chapter_slug'], self.test_chapter_slug)
        self.assertIsInstance(data['image_urls'], list)
        self.assertEqual(data['total_pages'], len(data['image_urls']))

        print(f"✓ Read chapter '{self.test_chapter_slug}' - Found {data['total_pages']} pages")

    # def test_08_export_pdf(self):
    #     """Test PDF export functionality"""
    #     if not hasattr(self, 'test_chapter_slug'):
    #         # Get a chapter slug from comic details
    #         if not hasattr(self, 'test_slug'):
    #             search_response = requests.get(f"{self.BASE_URL}/search?q=batman")
    #             search_data = search_response.json()
    #             if search_data['results']:
    #                 self.test_slug = search_data['results'][0]['slug']
    #             else:
    #                 self.skipTest("No search results available")

    #         details_response = requests.get(f"{self.BASE_URL}/details/{self.test_slug}")
    #         details_data = details_response.json()
    #         if details_data['chapters']:
    #             self.test_chapter_slug = details_data['chapters'][0]['slug']
    #         else:
    #             self.skipTest("No chapters available for testing")

    #     print(f"Testing PDF export for chapter: {self.test_chapter_slug}")
    #     response = requests.post(f"{self.BASE_URL}/export-pdf/{self.test_chapter_slug}")

    #     # PDF export might take time, so we allow for longer timeout
    #     if response.status_code == 200:
    #         self.assertEqual(response.headers['Content-Type'], 'application/pdf')
    #         self.assertGreater(len(response.content), 1000)  # PDF should be substantial
    #         print(f"✓ PDF export successful - Size: {len(response.content)} bytes")
    #     else:
    #         # If PDF export fails, it might be due to image loading issues
    #         data = response.json()
    #         self.assertIn('error', data)
    #         print(f"⚠ PDF export failed (expected): {data['error']}")

    def test_09_invalid_endpoints(self):
        """Test invalid endpoints return 404"""
        response = requests.get(f"{self.BASE_URL}/nonexistent")
        self.assertEqual(response.status_code, 404)

        data = response.json()
        self.assertIn('error', data)
        print("✓ Invalid endpoint properly returns 404")

    def test_10_invalid_slug(self):
        """Test invalid slug handling"""
        response = requests.get(f"{self.BASE_URL}/details/nonexistent-comic-slug")
        # This should either return 404 or 500 depending on the website response
        self.assertIn(response.status_code, [404, 500])

        data = response.json()
        self.assertIn('error', data)
        print("✓ Invalid slug properly handled")

class APILoadTest(unittest.TestCase):
    """Basic load testing"""
    BASE_URL = "http://localhost:5000/api"

    def test_concurrent_health_checks(self):
        """Test multiple concurrent requests"""
        import concurrent.futures

        def make_request():
            response = requests.get(f"{self.BASE_URL}/health")
            return response.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        success_count = sum(results)
        self.assertEqual(success_count, 10)
        print(f"✓ Load test - {success_count}/10 concurrent requests successful")

def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(ComicAPITestCase))
    suite.addTests(loader.loadTestsFromTestCase(APILoadTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\n{'='*50}")
    print("TESTS SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

if __name__ == '__main__':
    print("Comic API Integration Tests")
    print("=" * 50)
    print("Make sure Flask server is running on localhost:5000")
    print("These tests will make real HTTP requests to the API")
    print("=" * 50)

    try:
        # Quick connectivity test
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running, starting tests...\n")
            run_tests()
        else:
            print("✗ Server responded with error, check Flask server")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Flask server at localhost:5000")
        print("Please start the Flask server first with: python app.py")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
