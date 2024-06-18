const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

app.use(express.json());

app.post('/recommend-jobs', async (req, res) => {
    const skills = req.body.skills;

    if (!skills) {
        return res.status(400).send({ error: 'Skills input is required' });
    }

    try {
        const response = await axios.post('http://localhost:5000/recommend-jobs', { skills });
        res.send(response.data);
    } catch (error) {
        console.error(`Error communicating with Flask server: ${error}`);
        res.status(500).send({ error: 'Error communicating with recommendation server' });
    }
});

app.listen(port, () => {
    console.log(`Job recommendation API listening at http://localhost:${port}`);
});
