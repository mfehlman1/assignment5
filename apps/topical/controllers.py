from py4web import action, request, URL, abort
from .common import auth
from .models import db, parse_post_content, get_user_email

# Complete. 
@action("index", method=["GET"])
@action.uses("index.html", auth)
def index():
    return {}

@action('user_info', method=['GET'])    
@action.uses(auth)
def user_info():
    return {"user_id": auth.current_user.get("id") if auth.current_user else None}

@action('create_post', method=['POST'])
@action.uses(auth)
def create_post():
        if not auth.current_user:
            abort(403, "You must be logged in in order to make a post")
        content = request.json.get('content')
        if not content:
            return {"Must have post content"}
        
        post_id= db.post.insert(content=content)
        return {"message": "Post created", "post_id": post_id}

@action('get_posts', method=['GET'])
def get_posts():
    posts= db(db.post).select(orderby=~db.post.created_at).as_list()
    for post in posts:
        tags = db(
            (db.post_tag.post_id == post['id']) & (db.post_tag.tag_id == db.tag.id)
        ).select(db.tag.name).as_list()
        post['tags'] = [tag['name'] for tag in tags]
    return {"posts": posts}

@action('delete_post/<post_id>', method=['DELETE'])
@action.uses(auth)
def delete_post(post_id):
    try:
        post_id = int(post_id)
        post = db.post(post_id)
        if not auth.current_user:
            abort(403, "You must be logged in in order to make a post")
        post = db.post(post_id)
        if not post:
            return {"error": "Couldn't find post"}
        if post.user_id != auth.current_user.get("id"):
            return{"error": "Not authorized"}
        
        db(db.post.id == post_id).delete()
        return{"message": "Post deleted successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()  # Log the traceback
        return {"error": str(e)}

@action('get_tags', method=['GET'])
@action.uses(db)
def get_tags():
   active_tags = db(db.tag.id.belongs(db(db.post_tag.tag_id > 0)._select(db.post_tag.tag_id))).select(db.tag.ALL)
    return dict(tags=[{"id": tag.id, "name": tag.name} for tag in active_tags])

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