# Newsfeed - web based chat at real time
## Short description

- The system supports registration with username and password. After the logging in each user sees a common chat stream. 
- The user is able to like messages and block another user. The messages writen by blocked users cannot be seen by the the current user. 
- There is a rating based on the number of user liked comments divided into the square root of the user blockings.

## Technologies:

- server side - Python 3.4
- client side - HTML5, CSS3, JavaScript
- database - MongoDB

## How to use
- Install [python 3.4](https://www.python.org/download/releases/3.4.0/)
- Install [MongoDB](http://docs.mongodb.org/manual/installation/)
- git clone https://github.com/Meri-em/Newsfeed.git
- mongod --dbpath="../db"
- python main.py
