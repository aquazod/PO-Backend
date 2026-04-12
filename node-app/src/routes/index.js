const express = require('express');
const router = express.Router();

const listingsEndPoint = require('../controllers/listings.controller');
const scrappingEndPoint = require('../controllers/scrape.controller');
const metaEndPoint = require('../controllers/meta.controller');
 
router.get('/meta', metaEndPoint.getData);
router.get('/listings', listingsEndPoint.getData);
router.post('/scrape', scrappingEndPoint.createData);

module.exports = router;