from py4web import action, request, URL
from .common import auth
from .models import db, parse_post_content, get_user_email

# Complete. 
@action('create_post', method=['POST'])
@auth.requires_login()
def create_post():
    content = request.json.get('content')
    if not content:
        return {"Must have post content"}
    
    post_id= db.post.insert(content=content)
    return {"message": "Post created", "post_id": post_id}

@action('get_posts', method=['GET'])
def get_posts():
    posts= db(db.post).select(orderby=~db.post.created_at).as_list()
    return {"posts": posts}

@action('delete_post/<post_id>', method=['DELETE'])
@auth.requires_login()
def delete_post(post_id):
    post = db.post(post_id)
    if not post:
        return {"error": "Couldn't find post"}
    if post.user_id != auth.current_user.get("id"):
        return{"error": "Not authorized"}
    
    db(db.post_id == post_id).delete()
    return{"message": "Post deleted successfully"}

@action('get_tags', method=['GET'])
def get_tags():
    tags=db(db.tag).select().as_list()
    return {"tags": tags}

@action('toggle_tag', method=['POST'])
def toggle_tag():
    tag_name= request.json.get('tag_name')
    if not tag_name:
        return {"error": "No tag name"}
    tag = db(db.tag_name == tag_name.lower()).select().first()
    if not tag:
        return {"error": "Tag not found"}
    
@action('filter_posts', method=['POST'])
def filter_posts():
    tags= request.json.get('tags', [])
    if not tags:
        return {"error": "No tags provided"}
    query = (db.post.id ==db.post_tag.post_id) & (db.tag.id == db.post_tag.tag_id) & (db.tag.name.belongs(tags))
    posts = db(query).select(db.post.ALL, orderby=~db.post.created_at).as_list()
    return {"posts": posts}