from pymongo import MongoClient
import os
import bcrypt
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_mongodb():
    try:
        mongodb_url = os.getenv('MONGODB_URL')
        if not mongodb_url:
            print("❌ Error: MONGODB_URL not found in .env file")
            return None, None
        
        print("📡 Connecting to MongoDB...")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.server_info()
        
        db = client.court_db
        collections = {}
        
        # Initialize collections
        collections['users'] = db.users
        collections['cases'] = db.cases
        collections['hearings'] = db.hearings
        collections['documents'] = db.documents
        
        # Create indexes
        try:
            collections['users'].create_index("username", unique=True)
            collections['cases'].create_index("case_number", unique=True)
            collections['hearings'].create_index([("case_id", 1), ("date", 1)])
            print("✅ Database indexes created successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Error creating indexes: {str(e)}")
        
        print("✅ MongoDB connected successfully!")
        print(f"📊 Connected to database: {db.name}")
        
        # Initialize default users if none exist
        if collections['users'].count_documents({}) == 0:
            try:
                print("📝 Creating default users...")
                collections['users'].insert_many([{
                    "username": "admin",
                    "password": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
                    "role": "admin",
                    "email": "admin@court.com",
                    "created_at": datetime.datetime.utcnow()
                }, {
                    "username": "user",
                    "password": bcrypt.hashpw(b"user123", bcrypt.gensalt()),
                    "role": "user",
                    "email": "user@court.com",
                    "created_at": datetime.datetime.utcnow()
                }])
                print("✅ Default users created successfully!")
            except Exception as e:
                print(f"❌ Error creating default users: {str(e)}")
        
        return client, db
        
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
        print("\n🔍 Debug Information:")
        print("- Check if MongoDB Atlas is accessible")
        print("- Verify your IP is whitelisted in MongoDB Atlas")
        print("- Confirm username and password are correct")
        print("- Make sure your cluster is running")
        print(f"- Full error: {str(e)}")
        return None, None
