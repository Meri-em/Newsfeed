from pymongo import MongoClient
import gridfs
import io

client = MongoClient()
db = client.newsfeed
fs = gridfs.GridFS(db)
with open('D:\\Python0\\Newsfeed\\default_avatar.jpg', mode='rb') as f:
    fs.put(f, filename="default_avatar", desciption="default avatar")