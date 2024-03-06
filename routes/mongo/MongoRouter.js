const express = require('express');
const MongoController = require('../../controller/mongo/MongoController');

let MongoRouter = express.Router();

MongoRouter.get('/', MongoController.getProductsList);

module.exports = MongoRouter;

// Endpoint to trigger product syncing
// app.get('/mongo', async (req, res) => {
//     try {
//         const database = client.db('test');
//         const movies = database.collection('product');
//         // Query for a movie that has the title 'Back to the Future'
//         const query = { name: 'duck lamp' };
//         const movie = await movies.find(query);
//         for await (const doc of movie) {
//             console.log(doc);
//         }
//     } finally {
//         // Ensures that the client will close when you finish/error
//         await client.close();
//     }
// }); 