# Task Backend

A full-stack application for scraping and managing property listings, with a Node.js REST API backend and Python web scraper.

## Project Structure

```
Backend/
├── node-app/                 # Express.js REST API
│   ├── src/
│   │   ├── app.js           # Express app setup
│   │   ├── server.js        # Server entry point
│   │   ├── controllers/     # Route controllers
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── tests/
│
└── scraper/                  # Python Scrapy spider
    ├── run_spider.py        # Spider runner script
    ├── scraper/
    │   ├── items.py         # Scrapy item definitions
    │   ├── spiders/
    │   │   └── properties_spider.py  # Main spider
    │   └── logs/
    └── data/
        ├── listings.json    # Scraped listings data
        └── meta.json        # Scraper metadata
```

## Features

- **Web Scraping**: Python Scrapy spider that crawls property listings
- **REST API**: Express.js API for querying listings with filtering and pagination
- **Filtering**: Price range, date range, location, and keyword search

## Prerequisites

- Node.js (v14+) and npm
- Python (v3.8+) and pip
- Scrapy framework

## Installation

### Node.js Setup

```bash
cd node-app
npm install
```

### Python Setup

```bash
pip install -r requirements.txt
```

## Usage

### Start the API Server

Development mode (with auto-reload):
```bash
cd node-app
npm run dev
```

Production mode:
```bash
cd node-app
npm start
```

The server will run on `http://localhost:3000`

### Run the Web Scraper

```bash
python scraper/run_spider.py
```

This will:
1. Run the Scrapy spider to crawl property listings
2. Save results to `scraper/data/listings.json`
3. Update metadata in `scraper/data/meta.json`

## API Endpoints

### Get Listings

`GET /api/listings`

**Query Parameters:**
- `minprice` (number): Filter listings with price >= minprice
- `maxprice` (number): Filter listings with price <= maxprice
- `startdate` (YYYY-MM-DD): Filter listings posted after this date
- `enddate` (YYYY-MM-DD): Filter listings posted before this date
- `location` (string): Filter by exact location (case-insensitive)
- `search` (string): Search term to match in title or location
- `per_page` (number): Results per page (default: 10)
- `pg` (number): Page number (default: 1)

**Example:**
```
GET /api/listings?minprice=50000&maxprice=500000&per_page=20&pg=1
```

**Response:**
```json
{
  "total": 150,
  "per_page": 20,
  "pg": 1,
  "total_pages": 8,
  "show_pagination": true,
  "listings": [
    {
      "title": "Property Title",
      "price": 250000,
      "date": "2024-01-15",
      "location": "City, State",
      "link": "https://example.com/property"
    }
  ]
}
```

### Get Metadata

`GET /api/meta`

Returns scraper metadata including:
- Last scrape time
- Total listings scraped
- Scrape duration

## CORS Configuration

The API is configured to accept requests from:
- `http://localhost`
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8080`
- `http://localhost:443`

To add more origins or change for production, modify the CORS configuration in `node-app/src/app.js`.

## Development

### Adding New Filters

Edit `node-app/src/controllers/listings.controller.js` in the `getData` function.

### Modifying the Spider

Edit `scraper/scraper/spiders/properties_spider.py` to change:
- Target URL
- Scraping selectors
- Data extraction logic

### Updating Item Fields

Modify `scraper/scraper/items.py` to add or change scraped item fields.

## Troubleshooting

**CORS Errors:** Make sure your frontend origin is added to the CORS allowed origins list.

**Spider fails:** Check `scraper/scraper/logs/spider.log` for detailed error messages.

**"Cannot read properties of undefined":** Ensure scraped data has all expected fields (title, location, price, date).

## Dependencies

### Node.js
- `express` - Web framework
- `cors` - CORS middleware

### Python
- `scrapy` - Web scraping framework

