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
        self.prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
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


def fetch_islands():
    return [each.to_dict()["id"] for each in island_ref.db.order_by("id").stream()]


def fetch_residents(island_name):
    """Fetch residents by direct document lookup (O(1) instead of O(n))."""
    doc = island_ref.db.document(island_name).get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("residents", [])
    return None


def is_registered(username):
    home_island = find_home_island(username)
    return home_island if home_island else False


def remove_resident(username, island_name):
    """Remove a resident from an island. Returns True on success, False otherwise."""
    island = Island(island_name)
    island.pull()
    username_str = str(username)
    if username_str in island.residents:
        island.residents.remove(username_str)
        island.push()
        return True
    return False


def island_exists(island_name):
    """Check island existence by direct document lookup (O(1) instead of O(n))."""
    doc = island_ref.db.document(island_name).get()
    return doc.exists


def find_home_island(username):
    """Find user's home island using array_contains query (O(1) with index)."""
    username_str = str(username)
    query = island_ref.db.where("residents", "array_contains", username_str)
    results = list(query.stream())
    if results:
        return results[0].to_dict().get("id")
    return None


def highest_price(current_slot):
    query = island_ref.db.order_by("id")
    temp_dict = {}
    for each in query.stream():
        user_entry = each.to_dict()
        residents = user_entry.get("residents", [])
        prices = user_entry.get("prices", [])
        if not residents or len(prices) <= current_slot:
            continue
        price = prices[current_slot]
        if price and price > 0:
            temp_dict[residents[0]] = price
    if not temp_dict:
        return None
    return max(temp_dict.items(), key=operator.itemgetter(1))
