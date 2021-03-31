from pymongo import MongoClient
import os

PASS = os.getenv('MONGO_PASSWORD')
USER = os.getenv('MONGO_USER')

# Create connection to MongoDB
client = MongoClient('172.30.0.10', 27017 , username=USER, password=PASS)
setting = client['settingdb']
settingcol = setting['settings']

# Clear settings

client.drop_database(setting)

# Insert the settings into Mongo

settingcol.insert_many([
    { 'name' : "prefix", 'value' : "./", 'Description' : 'Sets the command prefix' }, 
    { 'name' : "muted_role",  'value' : 802721664365232158, 'Description' : 'Role users get when they are muted' } ,
    { 'name' : "command_channel_id" , 'value' : 797996052074201088, 'Description': 'channel where commands sould be done'},
    { 'name' : "log_channel_id", 'value' : 788119131068301335, 'Description': 'Channel where log results go' }])

counts = settingcol.find({},{ "addresses": { "$slice": [0, 1] } ,'_id': 0})
for key in counts:
    print(key)