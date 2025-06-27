import datetime as dt


from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DateTimeField,
    IntegerField,
    ForeignKeyField,
)

from peewee import DatabaseError

from config import DB_PATH


db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField(max_length=1024)


class RequestHistory(BaseModel):
    id = IntegerField(primary_key=True)
    title = CharField(max_length=1024)
    timestamp = DateTimeField(default=dt.datetime.now)

    # relation
    user = ForeignKeyField(User, backref='request_history')


class Favorite(BaseModel):
    id = IntegerField(primary_key=True)
    title = CharField(max_length=1024)
    timestamp = DateTimeField(default=dt.datetime.now)

    # relations
    user = ForeignKeyField(User, backref='favorite')


class Database:
    _db = db

    @classmethod
    def get_user(cls, username: str) -> User | None:
        return User.get_or_none(username=username)

    @classmethod
    def create_user(cls, username: str) -> User | None:
        try:
            user = User.create(username=username)

        except DatabaseError:
            return None

        return user

    @classmethod
    def is_user_exists(cls, id_: int) -> bool:
        return User.get(id=id_).exists()

    @classmethod
    def get_request_history(cls, username: str,
                            count: int = 10) -> list[RequestHistory]:
        return RequestHistory.filter(user__username=username).order_by(
            RequestHistory.timestamp.desc()).limit(count)

    @classmethod
    def create_request_history(cls, request_title: str,
                               username: str) -> RequestHistory:
        user = User.get_or_none(username=username)
        if not user:
            raise Exception("User not found")

        req = RequestHistory(title=request_title, user=user)
        req.save()
        return req

    @classmethod
    def get_favorites(cls, username: str, count: int = 10, offset: int = 0) -> list[Favorite]:
        return Favorite.select().join(User).where(User.username == username).order_by(Favorite.timestamp.desc()).offset(offset).limit(count)

    @classmethod
    def get_favorites_count(cls, username: str):
        return Favorite.select().join(User).where(User.username == username).count()

    @classmethod
    def add_to_favorites(cls, username: str, game_title: str) -> Favorite:
        user = User.get_or_none(username=username)
        if not user:
            raise Exception("User not found")

        fav = Favorite.get_or_none(title=game_title, user=user)
        if not fav:
            fav = Favorite(title=game_title, user=user)
            fav.save()

        return fav

    @classmethod
    def remove_from_favorites(cls, username: str, game_title: str) -> Favorite | None:
        user = User.get_or_none(username=username)
        if not user:
            raise Exception("User not found")

        fav = Favorite.get_or_none(title=game_title, user=user)
        if fav:
            fav.delete_instance()

        return fav

    @classmethod
    def create_favorite(cls, favorite_title: str) -> Favorite:
        fav = Favorite(title=favorite_title)
        fav.save()
        return fav

    @classmethod
    def create_models(cls) -> None:
        cls._db.create_tables(BaseModel.__subclasses__())

