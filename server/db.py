from pymongo import MongoClient
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from datetime import datetime
from gridfs import GridFS
# from flask import send_file
from io import BytesIO
from PIL import Image
from bson.objectid import ObjectId

def id(sth):
    return {'_id': ObjectId(sth['_id'])}

def id(sth):
    return {'_id': ObjectId(sth['_id'])}

def is_dict(sth):
    return type(sth) == type(dict())

class NewsfeedDB():
    def __init__(self):
        db = MongoClient().newsfeed
        self.grid_fs = GridFS(db)
        self._db = db
        self.fs = db.fs
        self.users = db.users
        self.messages = db.messages


    def find_user(self, user):
        return self.users.find_one({'username': user})

    def blocked_users(self, user):
        return self.find_user(user)['blocked_users']

    def view_profile(self, user):
        return self.users.find_one({'username': user}, {"password": 0})

    def add_user(self, username, password):
        return self.users.insert({
            'username': username,
            'password': generate_password_hash(password),
            'blocked_users': [],
            'number_of_likes': 0,
            'number_of_blocks': 0
        })

    def get_messages(self, user, limit=20):
        query = {'author': {'$nin': list(self.blocked_users(user))}}
        return self.messages.find(query).sort([("date_time", -1)]).limit(limit)

    def get_users(self):
        return self.users.find({}, {'password': 0, '_id': 0})

    def add_message(self, user, message):
        return self.messages.insert({
            "author": user,
            "message": message,
            "date_time": datetime.utcnow(),
            "likes": []
        })

    def like_message(self, user, message_id):
        message = self.messages.find_one({'_id': ObjectId(message_id)})
        if message:
            update = self.messages.update(id(message), {"$addToSet": {"likes": user}})
            if update['nModified']:
                self.users.update({'username': message['author']}, {'$inc': {'number_of_likes': 1}})
        return

    # def unlike_message(self, user, message):
    #     return self.messages.update(id(message), {"$pull": {"likes": user}})

    def muted(self, user):
        return self.users.find_one({'username': user}, {"muted": 1})

    # def notifications(self, user):
    #     return self.users.find_one({"_id": user['_id']}, {"notifications": 1})

    def block_user(self, user, blocked_user):
        update = self.users.update({'username': user}, {'$addToSet': {'blocked_users': blocked_user}})
        if update['nModified']:
            self.users.update({'username': blocked_user}, {'$inc': {'number_of_blocks': 1}})
        return

    def unblock_user(self, user, blocked_user):
        update = self.users.update({'username': user}, {'$pull': {'blocked_users': blocked_user}})
        if update['nModified']:
            self.users.update({'username': blocked_user}, {'$inc': {'number_of_blocks': -1}})
        return

    # def mute_user(self, user, other):
    #     return self.users.update({"username": user.username}, {"$addToSet": {"muted": other.username}})

    # def unmute_user(self, user, other):
    #     return self.users.update({"username": user.username}, {"$pull": {"muted": other.username}})

    def get_avatar(self, username):
        if self.fs.files.find_one({"filename": username}):
            im_stream = self.grid_fs.get_last_version(username)
        else:
            im_stream = self.grid_fs.get_last_version("default_avatar",\
                                         desciption="default avatar")
        im = Image.open(im_stream)
        img_io = BytesIO()
        im.save(img_io, 'JPEG', quality=70)
        img_io.seek(0)
        return img_io
        # return send_file(img_io, mimetype='image/jpeg')

    def update_avatar(self, user, file):
        self.fs.files.remove({"filename": user})
        with self.grid_fs.new_file(filename=user) as fp:
            fp.write(file)


    # def dismiss_notification(self, user):
    #     return self.users.update(user, {$pull: notifications: time: new Date(data.time)})


    # def change_avatar(self, user):
    #     return self.users.update(user, {$set: avatar: data.image})

# def add_post(self, ):
#     return posts.insert({author: user.username, content: data.content, date: new Date(), likes: 0})

  # likePost: (res, data, user) ->
  #   if data.id not in user.likes
  #     posts.findOne _id: ObjectID(data.id), (err, post) ->
  #       respond(res)(err, post)
  #       users.update {_id: user._id}, {$addToSet: likes: data.id}
  #       users.update {username: post.author}, {$addToSet: notifications: {user: user.username, likedPost: post.content, time: new Date()} }
  #       posts.update {_id: ObjectID(data.id)}, {$inc: likes: 1}