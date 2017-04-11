from pony.orm import *
from urllib.parse import quote
from isitornot.db import PonyDatabase

db = PonyDatabase()


class Community(db.Entity):
    slug = Required(str, 16, unique=True, py_check=lambda val: val == quote(val))  # The main name for the community
    name = Optional(str)  # An optional display name which can contain characters not allowed in a slug
    description = Optional(LongStr)  # An optional description for the community. This can be markdown.
    owner = Required(str)
    tags = Set('Tag')  # could be a json list which would be smaller in the database, but this gives us automatic secondary indices

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name if self.name is not "" else self.slug,
            'description': self.description,
            'owner': self.owner,
            'tags': [t.tag for t in self.tags]
        }


class Tag(db.Entity):
    tag = PrimaryKey(str)
    communities = Set(Community)
