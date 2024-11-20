"""
This file defines the database models
"""
import datetime
import re

from .common import db, Field, auth
from pydal.validators import *

#function for getting user email
def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

#function for getting user id
def get_user():
    return auth.current_user.get('id') if auth.current_user else None

#function for getting creation log
def get_time():
    return datetime.datetime.now(datetime.timezone.utc)

# Complete. 

# model for representing a post in a field
db.define_table(
    'post',
    Field('user_id', 'reference auth_user', default=get_user, readable=False, writable=False),
    Field('content', 'text', requires=IS_NOT_EMPTY(), label='Post Content'),
    Field('created_at', 'datetime', default=get_time, readable=False, writable=False),
    format='%(content)s'
)

#model for representing a tag in a field
db.define_table(
    'tag',
    Field('name', 'string', unique=True, requires=[IS_NOT_EMPTY(), IS_SLUG()]),
    format='%(name)s'
)

#interaction table for posts and tags
db.define_table(
    'post_tag',
    Field('post_id', 'reference post', requires=IS_IN_DB(db, 'post.id')),
    Field('tag_id', 'reference tag', requires=IS_IN_DB(db, 'tag.id'))
)

#function for parsing hashtags from posts
def parse_post_content(post_content):
    return re.findall(r"#(\w+)", post_content)

#Function for handling creation of tags along with its functionality
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
#function for handling all tag removal
def remove_tags(row):
        db(db.post_tag.post_id == getattr(row, 'id', None)).delete()
        unused_tags = db(~db.tag.id.belongs(db(db.post_tag.tag_id)._select(db.post_tag.tag_id))).select()
        for tag in unused_tags:
            db(db.tag.id == tag.id).delete()
db.post._after_delete.append(remove_tags)

#committing changes to database
db.commit()