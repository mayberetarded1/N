from pymongo import MongoClient

db = MongoClient('mongodb+srv://cybershareofficial:xagVsaMyGjfz2Vis@tablex.76cn5ex.mongodb.net/?retryWrites=true&w=majority')

users = db['main']['users']

def add_user(user_id):
    if users.find_one({'user_id': user_id}):
        return False
    else:
        users.insert_one({'user_id': user_id})
        return True
    
def get_user(user_id):
    if users.find_one({'user_id': str(user_id)}):
        return True
    else:
        return False
    
def remove_user(user_id):
    if users.find_one({'user_id': user_id}):
        users.delete_one({'user_id': user_id})
        return True
    else:
        return False