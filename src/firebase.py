from firebase_admin import credentials, firestore, initialize_app
from json import dumps, loads

from src.settings import KEY_CONTENTS
cred = credentials.Certificate(KEY_CONTENTS)
default_app = initialize_app(cred)


class DataBase(object):
    def __init__(self, database):
        db = firestore.client()
        self.db = db.collection(database)


turnip_ref = DataBase("turnips")


class Mayor(object):
    def __init__(self, username):
        self.id = username
        self.prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.purchased = 0
        self.purchase_price = 0

    def __repr__(self):
        return dumps(self.__dict__, default=dumper)

    def push(self):
        user_json = loads(self.__repr__())
        turnip_ref.db.document(self.id).update(user_json)

    def pull(self):
        user_json = turnip_ref.db.document(self.id).get().to_dict()
        for key in user_json:
            setattr(self, key, user_json[key])


def dumper(obj):
    return obj.__dict__


def is_registered(username):
    query = turnip_ref.db.order_by("id")
    for each in query.stream():
        if not (each.to_dict()["id"] == username):
            return False
    return True
