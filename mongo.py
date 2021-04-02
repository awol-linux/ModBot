from pymongo import MongoClient
import os

PASS = os.getenv('MONGO_PASSWORD')
USER = os.getenv('MONGO_USER')
mdbclient = MongoClient('mongodb', 27017, username=USER, password=PASS)
RemoveID = { "addresses": { "$slice": [0, 1] } ,'_id': 0}


class settings():
    def __init__(self, guild):
        self.test = 'test'
        self.guild_unsafe_name = str(guild.name).lower()
        self.namesafe = ''.join(e for e in self.guild_unsafe_name if e.isalnum())
        self.guildid = str(guild.id)
        self.setting = mdbclient['ModBot']
        self.settingcol = self.setting['settingdb-' + self.namesafe + self.guildid[-4]]


    def get(self, othersetting):
        terms = { 'name' : othersetting }       
        values = []
        for value in self.settingcol.find(terms, RemoveID):
            values.append(value['value'])
        if len(values) == 1:
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values

    def print_all(self):
       terms = {}
       values = []
       for value in self.settingcol.find(terms, RemoveID):
            values.append(value)
       return values

    def create(self, key, value, *description_array):
        terms = { 'name' : key }
        setting = { '$set' : { 'value' : value }}
        self.settingcol.update_one(terms, setting, upsert = True)
        if len(description_array) == 0:
            description_string = "No description given"
        else:
            description_string = " ".join(description_array)
        description = { '$set' : { 'Description' : description_string }}
        self.settingcol.update_one(terms, description, upsert = False)

    def update(self, key, value):
        if self.get(key):
            oldkey = self.get(key)
            terms = { 'name' : key }
            setting = { '$set' : { 'value' : value }}
            self.settingcol.update_one(terms, setting)
            out = { 'oldkey' : oldkey, 'newkey': self.get(key) }
            return out
    def get_description(self, name):
        terms = { 'name' : name }
        values = []
        for value in self.settingcol.find(terms, RemoveID):
            values.append(value['Description'])
        if len(values) == 1:
            print(values)
            return values[0]
        elif len(values) == 0:
            return None
        else:
            return values
