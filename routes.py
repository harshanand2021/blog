from app import app, db
from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User, Post

@app.route('/', methods=['GET'])
def home():
    return jsonify(message="Hello World!")

@app.route('/v1/register', methods=['POST'])
def register():

    data = request.get_json()

    if not data:
        return {"message": "Invalid request"}, 400

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return {"message": "Missing fields"}, 400

    user = User(email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(message="User registered"), 201

@app.route('/v1/login', methods=['POST'])
def login():

    data = request.get_json()
    if not data:
        raise BadRequest("Invalid request")

    email = data.get('email')
    password = data.get('password')

    token, _ = User.authenticate(email, password)
    if not token:
        raise BadRequest("Invalid credentials")

    return jsonify(access_token=token), 200

@app.route('/v1/posts', methods=['POST'])
@jwt_required()
def add_post():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    body = data.get('body')
    
    if not title or not body:
        raise BadRequest("Title and body are required")

    post = Post(title=title, body=body, author_id=user_id)
    db.session.add(post)
    db.session.commit()
    return jsonify(message="Post created"), 201

@app.route('/v1/posts/<int:post_id>', methods=['GET'])
def get_posts(post_id):
    post = Post.query.get(post_id)
    if not post:
        raise NotFound("Post not found")
    return jsonify(posts=post.to_dict()), 200

@app.route('/v1/posts/<int:post_id>', methods=['PATCH'])
@jwt_required()
def update_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get(post_id)
    if not post:
        raise NotFound("Post not found")
    if post.author_id != user_id:
        raise BadRequest("You are not authorized to modify this post")
    data = request.get_json()
    post.title = data.get('title', post.title)
    post.body = data.get('body', post.body)
    db.session.commit()
    return jsonify(message="Post updated"), 200