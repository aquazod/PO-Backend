const { spawn } = require('child_process');
const path = require('path');

exports.createData = (req, res) => {
  const pythonScript = path.join(__dirname, '../../../scraper/run_spider.py');
  const pythonProcess = spawn('python', [pythonScript]);

  let output = '';
  let error = '';

  pythonProcess.stdout.on('data', (data) => {
    output += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    error += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      res.json({ message: 'Scraping completed successfully', output: output });
    } else {
      res.status(500).json({ message: 'Scraping failed', error: error, code: code });
    }
  });

  pythonProcess.on('error', (err) => {
    res.status(500).json({ message: 'Failed to start scraper', error: err.message });
  });
};