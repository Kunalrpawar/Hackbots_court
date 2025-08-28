from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    try:
        # Get MongoDB URL from environment
        mongodb_url = os.getenv('MONGODB_URL')
        if not mongodb_url:
            print("❌ Error: MONGODB_URL not found in .env file")
            return False
            
        print(f"📡 Attempting to connect with URL: {mongodb_url}")
        
        # Try to connect
        client = MongoClient(mongodb_url)
        
        # Test connection by listing databases
        client.list_database_names()
        
        print("✅ Successfully connected to MongoDB!")
        print("📊 Available databases:", client.list_database_names())
        
        # Try to access our specific database
        db = client.court_db
        
        # Try to insert a test document
        result = db.test.insert_one({"test": "connection"})
        print("✅ Successfully inserted test document!")
        
        # Clean up test document
        db.test.delete_one({"test": "connection"})
        print("🧹 Cleaned up test document")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        print("\n🔍 Debug Information:")
        print("- Check if MongoDB Atlas is accessible")
        print("- Verify your IP is whitelisted in MongoDB Atlas")
        print("- Confirm username and password are correct")
        print("- Make sure your cluster is running")
        return False

if __name__ == "__main__":
    print("🔌 Testing MongoDB Connection...")
    test_mongodb_connection()
