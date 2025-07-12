from src.configs.config import engine
from functools import lru_cache
from sqlalchemy import Table, MetaData
from sqlalchemy.util import memoized_property

@lru_cache()
class Tables:
    def __init__(self):
        self.metadata = MetaData()
        self.metadata.bind = engine

    @memoized_property
    def users(self):
        return Table("users", self.metadata, autoload_with=engine)

    @memoized_property
    def chatrooms(self):
        return Table("chatrooms", self.metadata, autoload_with=engine)

    
    @memoized_property
    def chat_messages(self):
        return Table("chat_messages", self.metadata, autoload_with=engine)

    