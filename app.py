import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
)
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

# env path
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
# get env variables
MONGODB_URI = os.environ.get("MONGODB_CONNECTION_STRING")
DB_NAME = os.environ.get("DB_NAME")

# config for flask
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = '/static/profile_pics'

# secret key for user security
SECRET_KEY = 'YOUR_KEY'

# token cookie name
TOKEN_KEY = 'mytoken'

# database connection
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'id': payload.get('id')})
        if (not user_info):
            msg = 'There was a problem when logging you in'
            return redirect(url_for(
                'auth', msg=msg
            ))
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
        return redirect(url_for(
            'auth', msg=msg
        ))
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem when logging you in'
        return redirect(url_for(
            'auth', msg=msg
        ))
    
@app.route('/auth', methods=['GET'])
def auth():
    msg = request.args.get('msg')
    return render_template('auth.html', msg=msg, user_info=msg)

@app.route('/login', methods=['POST'])
def api_login():
    name_receive = request.form.get('name_give')
    pw_receive = request.form.get('password_give')
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({
        'id': name_receive,
        'password': pw_hash
    })
    if result:
        print(result['id'])
        my_datetime = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
        json_datetime = my_datetime.isoformat()
        payload = {
            'id': result['id'],
            'expired': json_datetime
        }
        token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
        print(token)
        return jsonify({
            'result': 'success',
            TOKEN_KEY: token
        })
    else:
        return jsonify({
            'result': 'fail',
            'msg': 'Login failed, check your id and password'
        })

@app.route('/register', methods=['POST'])
def api_register():
    name_receive = request.form.get('name_give')
    pw_receive = request.form.get('password_give')
    profile_pic_receive = request.form.get('profile_pic_give')

    print(name_receive, profile_pic_receive)
    
    if (not profile_pic_receive):
        profile_pic_receive = '/profile_pics/default.png'

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    doc = {
        'id': name_receive,
        'name': name_receive,
        'password': pw_hash,
        'profile_pic': profile_pic_receive
    }
    db.users.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': 'Your account registered'
    })

@app.route('/register/check-dup', methods=['POST'])
def check_dup():
    name_receive = request.form.get('name_give')
    exists = bool(db.users.find_one({'id': name_receive}))
    return jsonify({
        'exists': exists
    })

@app.route('/user/<username>', methods=['GET'])
def user(username):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        print(payload)
        status = username == payload.get('id')
        user_info = db.users.find_one(
            {'id': username,},
            {'_id': False}
        )
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username = payload.get('id')
        print(username)
        name_receive = request.form.get('name_give')
        about_receive = request.form.get('about_give')

        doc = {
            'name': name_receive,
            'profile_info': about_receive
        }
        post_doc = {
            'username': name_receive,
        }
        if 'file_give' in request.files:
            file = request.files.get('file_give')
            filename = secure_filename(file.filename)
            extension = filename.split('.')[-1]
            file_path = f'profile_pics/{username}.{extension}'
            file.save('./static/' + file_path)
            doc['profile_pic'] = file_path
            post_doc['profile_pic'] = file_path

        db.users.update_one(
            {'id': username},
            {'$set': doc}
        )

        db.posts.update_one(
            {'id': username},
            {'$set': post_doc}
        )

        return jsonify({
            'result': 'success',
            'msg': 'Your profile has been update'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))

@app.route('/posting', methods=['POST'])
def posting():

    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'id': payload.get('id')})
        comment_receive = request.form.get('comment_give')
        date_receive = request.form.get('date_give')
        doc = {
            'id': user_info.get('name'),
            'username': user_info.get('name'),
            'profile_pic': user_info.get('profile_pic'),
            'comment': comment_receive,
            'date': date_receive
        }
        db.posts.insert_one(doc)
        return jsonify({
            'result': 'success',
            'msg': 'Posting successful'
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/get_posts', methods=['POST'])
def get_posts():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        username_receive = request.args.get('username_give')
        if username_receive == '':
            posts = list(db.posts.find({}).sort('date', -1).limit(20))
        else: 
            posts = list(db.posts.find({'id': username_receive}).sort('date', -1).limit(20))
            
        for post in posts:
            post['_id'] = str(post['_id'])
            post['count_heart'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'heart'
            })
            post['heart-by-me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'heart',
                'user_id': payload.get('id')
            }))

            post['count_thumbs'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'thumbs'
            })
            post['thumbs-by-me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'thumbs',
                'user_id': payload.get('id')
            }))

            post['count_star'] = db.likes.count_documents({
                'post_id': post['_id'],
                'type': 'star'
            })
            post['star-by-me'] = bool(db.likes.find_one({
                'post_id': post['_id'],
                'type': 'star',
                'user_id': payload.get('id')
            }))
        print(posts)

        return jsonify({
            'result': 'success',
            'msg': 'Successful fetched all post',
            'posts': posts,
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'id': payload.get('id')})
        post_id_receive = request.form.get('post_id_give')
        type_receive = request.form.get('type_give')
        action_receive = request.form.get('action_give')

        doc = {
            'post_id': post_id_receive,
            'user_id': user_info.get('id'),
            'type': type_receive
        }

        if action_receive == 'add':
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)

        count = db.likes.count_documents({
            'post_id': post_id_receive,
            'type': type_receive
        })

        return jsonify({
            'result': 'success',
            'msg': 'Update successful',
            'count': count
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/secret', methods=['GET'])
def secret():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'id': payload.get('id')})
        return render_template('secret.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)