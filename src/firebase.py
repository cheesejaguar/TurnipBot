from firebase_admin import credentials, firestore, initialize_app
from json import dumps, loads
import operator

from src.settings import KEY_CONTENTS
cred = credentials.Certificate(KEY_CONTENTS)
default_app = initialize_app(cred)


class DataBase(object):
    def __init__(self, database):
        db = firestore.client()
        self.db = db.collection(database)


island_ref = DataBase("islands")


class Island(object):
    def __init__(self, island_name):
        self.id = island_name
        self.residents = []
        self.prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.purchased = 0
        self.purchase_price = 0

    def __repr__(self):
        return dumps(self.__dict__, default=dumper)

    def push(self):
        user_json = loads(self.__repr__())
        island_ref.db.document(self.id).update(user_json)

    def pull(self):
        user_json = island_ref.db.document(self.id).get().to_dict()
        for key in user_json:
            setattr(self, key, user_json[key])

    def create(self):
        user_json = loads(self.__repr__())
        island_ref.db.document(self.id).create(user_json)


def dumper(obj):
    return obj.__dict__


def is_registered(username):
    home_island = find_home_island(username)
    return home_island if home_island else False


def island_exists(island_name):
    query = island_ref.db.order_by("id")
    for each in query.stream():
        island = each.to_dict()
        if island_name == island["id"]:
            return True
    return False


def find_home_island(username):
    query = island_ref.db.order_by("id")
    for each in query.stream():
        # print(each.to_dict()["id"])
        for resident in each.to_dict()["residents"]:
            # print("{} vs {}".format(resident, username))
            if str(resident) == str(username):
                return each.to_dict()["id"]
    return None


def highest_price(current_slot):
    query = island_ref.db.order_by("id")
    temp_dict = {}
    for each in query.stream():
        user_entry = each.to_dict()
        temp_dict[user_entry["residents"][0]] = user_entry["prices"][current_slot]
    return max(temp_dict.items(), key=operator.itemgetter(1))
