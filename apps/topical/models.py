"""
This file defines the database models
"""
import datetime
import re

from .common import db, Field, auth
from pydal.validators import *

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.now(datetime.timezone.utc)

# Complete. 

# Model for representing a post in a field
db.define_table(
    'post',
    Field('user_id', 'reference auth_user', default=get_user, readable=False, writable=False),
    Field('content', 'text', requires=IS_NOT_EMPTY(), label='Post Content'),
    Field('created_at', 'datetime', default=get_time, readable=False, writable=False),
    format='%(content)s'
)

db.define_table(
    'tag',
    Field('name', 'string', unique=True, requires=[IS_NOT_EMPTY(), IS_SLUG()]),
    format='%(name)s'
)

db.define_table(
    'post_tag',
    Field('post_id', 'reference post', requires=IS_IN_DB(db, 'post.id')),
    Field('tag_id', 'reference tag', requires=IS_IN_DB(db, 'tag.id'))
)

def parse_post_content(post_content):
    return re.findall(r"#(\w+)", post_content)

def on_post_insert(fields, id):
    tags= parse_post_content(fields["content"])
    tag_ids= []

    for tag_name in tags:
        tag = db(db.tag.name == tag_name.lower()).select().first()
        if not tag:
            tag_id = db.tag.insert(name=tag_name.lower())
        else:
            tag_id = tag.id
        tag_ids.append(tag_id)
    
    for tag_id in tag_ids:
        db.post_tag.insert(post_id=id, tag_id=tag_id)
            
db.post._after_insert.append(on_post_insert)
db.post._after_delete.append(
    lambda row: ( 
        db(db.post_tag.post_id == getattr(row, 'id', None)).delete())
        db(db.tag.id.notin_(db(db.post_tag.tag_id > 0)._select(db.post_tag.tag_id))).delete(),
)

db.commit()