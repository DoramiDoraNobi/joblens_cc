// src/controllers/jobController.js
const { findMatchingJobs } = require('../services/jobService');

const searchJobs = async (req, res) => {
    const { skills } = req.body;
    try {
        const jobs = await findMatchingJobs(skills);
        res.json(jobs);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = { searchJobs };
