from pymongo import MongoClient
import os

PASS = os.getenv("MONGO_PASSWORD")
USER = os.getenv("MONGO_USER")
RemoveID = {"addresses": {"$slice": [0, 1]}, "_id": 0}


def start_db(func):
    """
    context manager for database object so it can be opened and closed for every function
    """

    def create_db_object(*args, **kwargs):
        called_class = args[0]
        mdbclient = MongoClient("mongodb", 27017, username=USER, password=PASS)
        botdb = mdbclient["ModBot"]
        called_class.action_item_coll = botdb["action_items"]
        print(args)
        if hasattr(args[0], "guild"):
            guild = args[0].guild
            guildname = "".join(e for e in str(guild.name).lower() if e.isalnum())
            guildid = str(guild.id)
            called_class.settingcol = botdb["settingdb-" + guildname + guildid[-4]]
        run = func(*args, **kwargs)
        mdbclient.close()
        return run

    return create_db_object


class action_items:
    def __init__(self):
        pass

    @start_db
    def get_action_pretty(self, action_item):
        """
        Runs a database query using the main action item and returns the pretty names
        Args:
            Action item
        Returns:
            All the pretty aliases
        """
        terms = {"name": action_item}
        values = []
        for value in action_item_coll.find(terms, RemoveID):
            values.append(value["value"])
        return values

    @start_db
    def get_action_item(self, action_pretty):
        """
        Runs a DB query using a pretty name and returns any related anction dict
        Args:
            action_pretty
        Returns:
            the Action dict
        """
        if len(action_pretty) == 0:
            terms = {}
        else:
            terms = {"prettys": " ".join(action_pretty)}
        values = []
        for value in action_item_coll.find(terms, RemoveID):
            print(value)
            values.append(value)
        return values

    @start_db
    def insert_table(self, data):
        """
        Pushes the action table into the db
        Args:
            data (action_table)
        Returns:
            Bool
        """
        return self.action_item_coll.insert_one(data)


class settings:
    def __init__(self, guild):
        self.guild = guild

    @start_db
    def get(self, othersetting):
        terms = {"name": othersetting}
        values = []
        for value in self.settingcol.find(terms, RemoveID):
            values.append(value["value"])
        print(values)
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values

    @start_db
    def print_all(self):
        terms = {}
        return [value for value in self.settingcol.find(terms, RemoveID)]

    @start_db
    def create(self, key, value, *description_array):
        terms = {"name": key}
        setting = {"$set": {"value": value}}
        self.settingcol.update_one(terms, setting, upsert=True)
        if len(description_array) == 0:
            description_string = "No description given"
        else:
            description_string = " ".join(description_array)
        description = {"$set": {"Description": description_string}}
        return self.settingcol.update_one(terms, description, upsert=False)

    @start_db
    def update(self, key, value, *description_array):
        if self.get(key):
            oldkey = self.get(key)
            terms = {"name": key}
            setting = {"$set": {"value": value}}
            self.settingcol.update_one(terms, setting)
            if len(description_array) == 0:
                description_string = "No description given"
            else:
                description_string = " ".join(description_array)
            description = {"$set": {"Description": description_string}}
            self.settingcol.update_one(terms, description, upsert=False)
            out = {"oldkey": oldkey, "newkey": self.get(key)}
            return out

    @start_db
    def get_description(self, name):
        terms = {"name": name}
        values = []
        for value in self.settingcol.find(terms, RemoveID):
            values.append(value["Description"])
        if len(values) == 1:
            print(values)
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values
