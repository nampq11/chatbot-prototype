from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://nampham11062002:phamnamaq123@cluster0.t13jleh.mongodb.net"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

print(client.list_database_names())
# create a new database and collection
database = client["test_database"]
collection = database["test_collection"]

# check if the database and collection were created
if "test_database" in client.list_database_names():
    print("Database created successfully.")
else:
    print("Database creation failed.")