// src/utils/modelUtils.js
const tf = require('@tensorflow/tfjs');
const path = require('path');

const loadModel = async () => {
    const modelPath = path.resolve(__dirname, 'path_to_model/model.json');
    const model = await tf.loadGraphModel(`file://${modelPath}`);
    return model;
};

const matchSkillsWithModel = async (userSkills) => {
    const model = await loadModel();
    const inputTensor = tf.tensor(userSkills, [1, userSkills.length]);
    const predictions = model.predict(inputTensor).dataSync();
    
    // Here we assume the predictions are IDs or indices of matching jobs.
    const jobIds = Array.from(predictions).map((score, index) => ({ id: index + 1, score }));

    // Placeholder for job data fetching based on predictions
    const jobs = jobIds.filter(job => job.score > 0.5).map(job => ({ id: job.id, title: `Job ${job.id}`, score: job.score }));
    
    return jobs;
};

module.exports = { matchSkillsWithModel };
