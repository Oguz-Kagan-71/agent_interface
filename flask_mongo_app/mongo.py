from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os, dotenv

# Load environment variables
dotenv.load_dotenv()

# create a db class
class db:
    def __init__(self):
        self.mongoUri = None
        self.connection = None
        self.collections = None

    def setup(self, mongoUri):
        self.mongoUri = mongoUri
        self.connection = self.connect_db()
        self.collections = self.get_collections()


    def connect_db(self):
        # Connect to MongoDB
        try:
            client = MongoClient(self.mongoUri)  # Seçilen URI ile bağlantı kur
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return None

        # Access the database
        try:
            db = client["db"]
            print("Accessed to db")
        except Exception as e:
            print(f"Error connecting to database: {e}")
        return db


    def get_collections(self):
        return self.connection.list_collection_names()
    
    def get_collection(self, collection):
        return self.connection[collection]
    
    def getMongoUri(self):
        return self.mongoUri
    
    def setMongoUri(self, MONGO_DB_URI):
        self.mongoUri = MONGO_DB_URI
        return self.mongoUri
    
    def checkConnection(self):
        try:
            res = self.connection.client.admin.command('ping')
        except ConnectionFailure:
            return {"mongoStatus": "-1", "error": str(ConnectionFailure)}
        return {"mongoStatus": "1"}

if __name__ == '__main__':
    db = db()
    print("DB Collections: ",db.collections)
