const { MongoClient, ServerApiVersion } = require('mongodb');
var username = encodeURIComponent("jmckenna49");
var password = encodeURIComponent("");

async function main() {
    var uri = `mongodb+srv://${username}:${password}@mycluster.4q5ij.mongodb.net/?retryWrites=true&w=majority&appName=MyCluster`;
    const client = new MongoClient(uri);
    console.log("Connecting")
    await client.connect();
    console.log("Connected")
    // await listDatabases(client);
    try {
        await client.connect();
        await retrieveUsers(client);
        // await listDatabases(client);
    
    } catch (e) {
        console.error(e);
    }

    finally {
        await client.close();
    }

}

main().catch(console.error);

async function listDatabases(client){
    databasesList = await client.db().admin().listDatabases();
 
    console.log("Databases:");
    databasesList.databases.forEach(db => console.log(` - ${db.name}`));
};

async function retrieveUsers(client){
    const db = client.db("user_data");
    const collection = db.collection("users");
    const result = await collection.find({}).toArray();
    console.log(result);
}
