// src/app.js
const express = require('express');
const jobRoutes = require('./routes/jobRoutes');

const app = express();

app.use(express.json());
app.use('/api/jobs', jobRoutes);

module.exports = app;
