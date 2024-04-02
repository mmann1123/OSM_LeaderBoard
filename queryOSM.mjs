// gets the number of nodes created by a list of users in a specific area
// execute:
// node queryOSM.mjs

// const fetch = require('node-fetch');
import fetch from 'node-fetch';

// Define the Overpass API endpoint
const OVERPASS_URL = "https://overpass-api.de/api/interpreter";

// Define the bounding box for Brooklyn, NY
const brooklyn_bbox = "40.551042, -74.05663, 40.739446, -73.833365";

// List of usernames to query
const usernames = [
    "mmann1123", "haycam", "I-Izzo", "isamah", "livmakesmaps",
    "kangaroo5445", "brikin", "caitnahc", "KQWilson", "o_paq", "DuckDuckCat"
];

// Function to perform the query for a single user
async function queryUser(username) {
    const query = `
        [out:json];
        (
          node(user:"${username}")(${brooklyn_bbox});
        );
        out count;
    `;

    try {
        const response = await fetch(OVERPASS_URL, {
            method: 'POST',
            body: new URLSearchParams({ data: query })
        });
        const data = await response.json();
        // Assuming the count is directly accessible; might need adjustment
        const count = data.elements ? data.elements[0].tags.nodes : "N/A";
        return { username, count };
    } catch (error) {
        console.error(`Query for user '${username}' failed`, error);
        return { username, count: "Error" };
    }
}

// Function to query all users and log results
async function queryAllUsers() {
    const results = await Promise.all(usernames.map(username => queryUser(username)));
    const userNodeCounts = results.reduce((acc, { username, count }) => {
        acc[username] = count;
        return acc;
    }, {});

    console.log("Node counts by user:", userNodeCounts);
}

// Execute the query for all users
queryAllUsers();
