import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

# List of URLs to test
URLS = [
    "https://reddensoft.com/blog",
    "https://reddensoft.com/edtech-software-development",
    "https://reddensoft.com/realestate-software-development",
    "https://reddensoft.com/healthcare-software-development",
    "https://reddensoft.com/partner-with-us",
    "https://reddensoft.com/hire-us",
    "https://reddensoft.com/automotive-software-development",
    "https://reddensoft.com/travel-hospitality-software-development",
    "https://reddensoft.com/foodtech-software-development",
    "https://reddensoft.com/our-leadership-team",
    "https://reddensoft.com/ecommerce-software-development",
    "https://reddensoft.com/graphic-design-services",
    "https://reddensoft.com/website-design-services",
    "https://reddensoft.com/fintech-software-development",
    "https://reddensoft.com/ui-ux-design-services",
    "https://reddensoft.com/web3-development-company",
    "https://reddensoft.com/digital-marketing-services",
    "https://reddensoft.com/paas-development-company",
    "https://reddensoft.com/app-development-company",
    "https://reddensoft.com/saas-development-company",
    "https://reddensoft.com/iaas-development-company",
    "https://reddensoft.com/hire-ai-ml-developers",
    "https://reddensoft.com/hire-wordpress-developers",
    "https://reddensoft.com/hire-woocommerce-developers",
    "https://reddensoft.com/hire-shopify-developers",
    "https://reddensoft.com/hire-angular-developers",
    "https://reddensoft.com/hire-drupal-developers",
    "https://reddensoft.com/hire-duda-developers",
    "https://reddensoft.com/hire-devops-developers",
    "https://reddensoft.com/hire-python-developers",
    "https://reddensoft.com/hire-react-developers",
    "https://reddensoft.com/hire-nextjs-developers",
    "https://reddensoft.com/hire-vue-developers",
    "https://reddensoft.com/hire-ios-app-developers",
    "https://reddensoft.com/hire-android-app-developers",
    "https://reddensoft.com/hire-full-stack-developers",
    "https://reddensoft.com/hire-mobile-app-developers",
    "https://reddensoft.com/hire-php-developers",
    "https://reddensoft.com/hire-codeigniter-developers",
    "https://reddensoft.com/hire-laravel-developers",
    "https://reddensoft.com/hire-figma-designers",
    "https://reddensoft.com/hire-adobe-xd-designers",
    "https://reddensoft.com/hire-ui-developers",
    "https://reddensoft.com/portfolio/robocent",
    "https://reddensoft.com/portfolio/candid-sync",
    "https://reddensoft.com/portfolio/trispire",
    "https://reddensoft.com/portfolio/origami",
    "https://reddensoft.com/contact",
    "https://reddensoft.com/ai-applications",
    "https://reddensoft.com/testimonials",
    "https://reddensoft.com/career",
    "https://reddensoft.com/start-a-project"
]

@pytest.fixture(scope="session")
def driver():
    """Setup Chrome driver with headless options - Railway/Docker compatible"""
    chrome_options = Options()
    
    # Essential headless options
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Additional stability options
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--single-process")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set Chrome binary location if provided
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
    if os.path.exists(chrome_bin):
        chrome_options.binary_location = chrome_bin
        print(f"[INFO] Using Chrome binary: {chrome_bin}")
    
    # Set ChromeDriver path if provided
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
    
    try:
        if os.path.exists(chromedriver_path):
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print(f"[INFO] Using ChromeDriver: {chromedriver_path}")
        else:
            # Fallback to default
            driver = webdriver.Chrome(options=chrome_options)
            print("[INFO] Using default ChromeDriver")
        
        driver.set_page_load_timeout(30)
        print("[SUCCESS] Chrome driver initialized successfully")
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize Chrome driver: {str(e)}")
        raise
    
    yield driver
    
    try:
        driver.quit()
        print("[INFO] Chrome driver closed successfully")
    except:
        pass

@pytest.mark.parametrize("url", URLS)
def test_url_status_and_load(driver, url):
    """Test each URL for status code 200 and successful page load"""
    
    # First, check status code with requests
    start_time = time.time()
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        status_code = response.status_code
        print(f"\n[INFO] Checking: {url}")
        print(f"[STATUS] HTTP Status Code: {status_code}")
        
        # Assert status code is 200
        assert status_code == 200, f"Expected status 200, got {status_code}"
        
    except requests.RequestException as e:
        pytest.fail(f"Failed to reach {url}: {str(e)}")
    
    # Then, load page with Selenium
    try:
        driver.get(url)
        
        # Wait for page to load (wait for body element)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("tag name", "body"))
        )
        
        load_time = time.time() - start_time
        
        # Get page title
        page_title = driver.title
        
        print(f"[SUCCESS] Page loaded successfully")
        print(f"[TITLE] {page_title}")
        print(f"[TIME] Load time: {load_time:.2f}s")
        
        # Assert page loaded (has title and body)
        assert page_title, "Page has no title"
        assert driver.find_element("tag name", "body"), "Page has no body element"
        
        print(f"✓ {url} - Status: {status_code} - Time: {load_time:.2f}s")
        
    except Exception as e:
        pytest.fail(f"Failed to load page {url}: {str(e)}")

def test_summary():
    """Print summary at the end"""
    print(f"\n{'='*80}")
    print(f"Test Summary: {len(URLS)} URLs tested")
    print(f"{'='*80}")