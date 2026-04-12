const fs = require('fs');
const path = require('path');

exports.getData = (req, res) => {
  try {
    const metaPath = path.join(__dirname, '../../../scraper/data/meta.json');
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
    res.json({ listings: meta });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};