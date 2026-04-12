const fs = require('fs');
const path = require('path');

exports.getData = (req, res) => {
  /**
   * Expected query parameters:
   * - minprice: minimum price filter
   * - maxprice: maximum price filter
   * - startdate: filter listings posted after this date (YYYY-MM-DD)
   * - enddate: filter listings posted before this date (YYYY-MM-DD)
   * - location: filter by location (case-insensitive)
   * - search: search term to match in title or location (case-insensitive)
   * - per_page: number of listings to return per page (default: 10)
   * - pg: page number for pagination (default: 1)
   */
  try {
    const listingsPath = path.join(__dirname, '../../../scraper/data/listings.json');
    const listings = JSON.parse(fs.readFileSync(listingsPath, 'utf8'));

    let filtered = listings;

    // Price range filter
    if (req.query.minprice || req.query.maxprice) {
      const minPrice = req.query.minprice ? parseInt(req.query.minprice) : 0;
      const maxPrice = req.query.maxprice ? parseInt(req.query.maxprice) : 10000000;
      filtered = filtered.filter(item => item.price && item.price >= minPrice && item.price <= maxPrice);
    }

    // Date range filter
    if (req.query.startdate || req.query.enddate) {
      const startDate = req.query.startdate ? new Date(req.query.startdate) : new Date(0);
      const endDate = req.query.enddate ? new Date(req.query.enddate) : new Date();
      filtered = filtered.filter(item => {
        const itemDate = new Date(item.date);
        return item.date && itemDate >= startDate && itemDate <= endDate;
      });
    }

    // Location filter
    if (req.query.location) {
      filtered = filtered.filter(item => item.location && item.location.toLowerCase() === req.query.location.toLowerCase());
    }

    // Search in title and location
    if (req.query.search) {
      const searchTerm = req.query.search.toLowerCase();
      filtered = filtered.filter(item =>
        (item.title && item.title.toLowerCase().includes(searchTerm)) ||
        (item.location && item.location.toLowerCase().includes(searchTerm))
      );
    }

    // Pagination
    const perPage = req.query.per_page ? parseInt(req.query.per_page) : 10;
    const page = req.query.pg && (filtered.length >= (perPage * parseInt(req.query.pg))) ? parseInt(req.query.pg) : 1;
    const startIndex = (page - 1) * perPage;
    const paginatedListings = filtered.slice(startIndex, startIndex + perPage);

    

    res.json({ 
      total: filtered.length,
      per_page: perPage,
      pg: page,
      total_pages: Math.ceil(filtered.length / perPage),
      show_pagination: filtered.length > perPage,
      listings: paginatedListings,
     });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};