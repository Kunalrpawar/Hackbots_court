from datetime import datetime
from bson import ObjectId

def create_user(username, password, role='user', email=None):
    return {
        'username': username.lower(),
        'password': password,  # In production, use password hashing
        'role': role,
        'email': email,
        'created_at': datetime.utcnow(),
        'last_login': None,
        'is_active': True
    }

def create_case(case_number, title, case_type, plaintiff, defendant, filed_by):
    return {
        'case_number': case_number,
        'title': title,
        'case_type': case_type,
        'plaintiff': plaintiff,
        'defendant': defendant,
        'filed_by': filed_by,  # User ID who filed the case
        'filing_date': datetime.utcnow(),
        'status': 'pending',  # pending, active, closed, etc.
        'documents': [],  # List of document IDs
        'hearings': [],  # List of hearing IDs
        'outcome': None,
        'last_updated': datetime.utcnow()
    }

def create_hearing(case_id, date, judge, court_room, hearing_type):
    return {
        'case_id': case_id,
        'date': date,
        'judge': judge,
        'court_room': court_room,
        'hearing_type': hearing_type,
        'status': 'scheduled',  # scheduled, completed, postponed, cancelled
        'notes': None,
        'attendees': [],
        'documents': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }

def create_document(case_id, title, document_type, uploaded_by):
    return {
        'case_id': case_id,
        'title': title,
        'document_type': document_type,
        'uploaded_by': uploaded_by,  # User ID
        'upload_date': datetime.utcnow(),
        'file_path': None,  # Path to stored file
        'status': 'pending',  # pending, verified, rejected
        'metadata': {},
        'tags': []
    }

# Database operation helpers
def get_case_by_number(db, case_number):
    return db.cases.find_one({'case_number': case_number})

def get_user_cases(db, user_id):
    return list(db.cases.find({
        '$or': [
            {'filed_by': user_id},
            {'plaintiff.id': user_id},
            {'defendant.id': user_id}
        ]
    }).sort('filing_date', -1))

def get_upcoming_hearings(db, user_id=None, days=30):
    query = {
        'date': {
            '$gte': datetime.utcnow(),
            '$lte': datetime.utcnow().replace(day=datetime.utcnow().day + days)
        },
        'status': 'scheduled'
    }
    if user_id:
        query['case_id'] = {'$in': get_user_cases(db, user_id)}
    
    return list(db.hearings.find(query).sort('date', 1))

def update_case_status(db, case_id, status):
    return db.cases.update_one(
        {'_id': ObjectId(case_id)},
        {
            '$set': {
                'status': status,
                'last_updated': datetime.utcnow()
            }
        }
    )
