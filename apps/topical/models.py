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
    return datetime.now(timezone.utc)

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
    'tag'
    Field('name', 'string', unique=True, requires=[IS_NOT_EMPTY(), IS_SLUG()]),
    format='%(name)s'
)

db.define_table(
    'post_tag'
    Field('post_id', 'reference post', requires=IS_IN_DB(db, 'post.id')),
    Field('tag_id', 'reference tag', requires=IS_IN_DB(db, 'tag.id'))
)

def parse_tags():
    return re.findall(r'#(\w+)', post_content)

def on_post_insert(fields):
    tags= parse_tags(fields['content'])
    tag_ids= []

    for tag_name in tags:
        tag, created= db.tag.get_or_insert(name=tag_name.lower())
        tag_ids.append(tag.id)
    
    for tag_id in tag_ids:
        db.post_tag.insert(post_id=fields['id'], tag_id=tag_id)
            
db.post._after_insert.append(on_post_insert)
db.post._after_delete.append(lambda row: db(db.post_tag.post_id == row.id).delete())

db.commit()