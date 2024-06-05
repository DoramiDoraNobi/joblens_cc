// src/services/jobService.js
const { matchSkillsWithModel } = require('../utils/modelUtils');

const findMatchingJobs = async (skills) => {
    const matchingJobs = await matchSkillsWithModel(skills);
    return matchingJobs;
};

module.exports = { findMatchingJobs };
