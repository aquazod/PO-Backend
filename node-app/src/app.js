const express = require('express');
const routes = require('./routes');
const cors = require('cors');

const app = express();

app.use(cors({
  origin: ['http://localhost', 'http://localhost:5173', 'http://localhost:3000', 'http://localhost:8080', 'http://localhost:443'],
  credentials: true
}));

app.use(express.json());
app.use('/api', routes);

module.exports = app;