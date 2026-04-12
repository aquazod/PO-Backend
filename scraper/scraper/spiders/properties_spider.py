"""
This file defines the scraping logic for the properties spider. It uses Scrapy to crawl the target website.
"""

import scrapy
import re
import logging
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse, urljoin

# Add parent directory to path so imports work when run as standalone spider
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scraper.items import PropertyItem

# Setup logging to file
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "spider.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


BASE_URL = "https://repossessedhousesforsale.com/properties/"

CLEAN_PRICE = re.compile(r"[^\d]")

DATE_PATTERN = re.compile(
    r"Added\s+on\s+(\d{1,2}\s+\w{3},?\s*\d{4})", re.IGNORECASE
)

DATE_FORMATS = ["%d %b, %Y", "%d %b %Y", "%d %B, %Y", "%d %B %Y"]

def parse_price(price_element: str) -> int | None:
    """Return price as an integer, or None if unparseable."""
    if not price_element:
        return None
    digits = CLEAN_PRICE.sub("", price_element.strip())
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        logging.warning(f"Could not parse price: {price_element}")
        return None
    
def parse_date(date_text: str) -> str | None:
    """
    Parse 'Added on DD Mon, YYYY' into an ISO date string (YYYY-MM-DD).
    Returns None if the date cannot be parsed.
    """
    if not date_text:
        return None
    match = DATE_PATTERN.search(date_text)
    if not match:
        # Fall back: try to parse the entire stripped string
        candidate = date_text.strip()
    else:
        candidate = match.group(1)

    # Normalize — remove trailing/leading spaces and commas
    candidate = candidate.strip().replace(",", "")

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    logging.warning(f"Could not parse date: {date_text}")
    return None

def make_absolute_url(url):
    """
    If 'url' is relative, convert it to an absolute URL using 'base_url'.
    If it's already absolute, return it unchanged.
    """
    parsed = urlparse(url)
    
    # If scheme or netloc exists, it's already absolute
    if parsed.scheme and parsed.netloc:
        return url
    
    return urljoin(BASE_URL, url)

def strip_pg_param(url: str) -> str:
    """Remove the ?pg= navigation parameter from a property link."""
    if not url:
        return url
    parsed = urlparse(url)
    params = {k: v for k, v in parse_qs(parsed.query).items() if k != "pg"}
    flat = {k: v[0] for k, v in params.items()}
    clean = parsed._replace(query=urlencode(flat) if flat else "")
    return urlunparse(clean)


class PropertiesSpider(scrapy.Spider):
    name = "properties"
    allowed_domains = ["repossessedhousesforsale.com"]

    
    custom_settings = {} # i could override this spider's settings here if needed, can be used for RETRIES and THROTTLING

    def __init__(self, start_page: int = 1, max_pages: int = 0):
        """
        start_page: first page to scrape (default 1)
        max_pages:  hard cap on pages scraped — 0 means no cap (full crawl)
        min_price:  lowest price seen, for fronend filtering
        max_price:  highest price seen, for frontend filtering
        """
        self.start_page = int(start_page)
        self.max_pages = int(max_pages)
        self.total_properties = 0
        self.total_pages = 0
        self.min_price = int(1e9)
        self.max_price = 0
        self.seen_properties = set()  # to avoid duplicates based on link

    def start_requests(self):
        yield scrapy.Request(
            url=f"{BASE_URL}?pg={self.start_page}",
            callback=self.parse,
            meta={"page": self.start_page},
        )

    def parse(self, response):
        page = response.meta["page"]

        # check if we reached the stop condition: non-200 response status code
        if response.status != 200:
            logging.error(f"Non-200 status {response.status} on page {page} — stopping.")
            return
        
        properties = response.css('[itemtype="https://schema.org/House"]')

        if not properties:
            logging.info(f"No properties found on page {page} — end of listings.")
            return
        
        self.total_pages += 1

        for property in properties:
            item = self._extract_item(property, page, response.url)
            if item is not None:
                self.total_properties += 1
                yield item

        # check if we reached the stop condition: max_pages limit
        if self.max_pages and page >= self.start_page + self.max_pages - 1:
            logging.info(f"Reached max_pages limit of {self.max_pages} — stopping.")
            return
        
        # go to next page
        next_page = page + 1
        yield scrapy.Request(
            url=f"{BASE_URL}?pg={next_page}",
            callback=self.parse,
            meta={"page": next_page},
        )


    def _extract_item(self, property, page, url) -> PropertyItem | None:
        try:
            item = PropertyItem()

            # start with link to check for duplicates, since it's the most reliable unique identifier
            link_element = property.css("a.properties-link::attr(href)").get()
            if link_element:
                link_absolute = make_absolute_url(link_element)
                link = strip_pg_param(link_absolute)
                if link in self.seen_properties:
                    return None
                self.seen_properties.add(link)
            else:
                item["link"] = None

            # Title
            title_element = property.css(".archive-properties-title-link::text").get()

            # return None if title is missing or empty, as it's a critical field
            if not title_element or not title_element.strip():
                return None
            
            item["title"] = title_element.strip()

            # Price
            price_element = property.css('[itemprop="value"]::text').get()
            item["price"] = parse_price(price_element)

            self.min_price = min(item["price"], self.min_price) if item["price"] is not None else self.min_price
            self.max_price = max(item["price"], self.max_price) if item["price"] is not None else self.max_price

            # Date
            property_date = None
            for text in property.css("*::text").getall():
                if "Added on" in text or "added on" in text.lower():
                    property_date = text
                    break
            item["date"] = parse_date(property_date)

            # Location
            address_element = property.css('[itemprop="address"]::text').get()
            if address_element:
                item["location"] = address_element.strip()
            else:                
                item["location"] = None

            return item
        except Exception as e:
            logging.error(f"Error extracting item on page {page} ({url}): {e}")
            return None