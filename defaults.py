from pymongo import MongoClient
import os
import asyncio

PASS = os.getenv('MONGO_PASSWORD')
USER = os.getenv('MONGO_USER')

# Create connection to MongoDB
client = MongoClient('mongodb', 27017 , username=USER, password=PASS)

async def set_defaults(guild, channel_id="", admin_roles='', muted_role=""):
    guildname = str(guild.name).lower()
    namesafe = ''.join(e for e in guildname if e.isalnum())
    guildid = str(guild.id)
    setting = client['ModBot']
    settingcol = setting['settingdb-' + namesafe + guildid[-4]]

    # Clear settings

    client.drop_database(setting)

    # Insert the settings into Mongo

    settingcol.insert_many([
        { 'name' : "prefix", 'value' : "./", 'Description' : 'Sets the command prefix' }, 
        { 'name' : "admin_roles",  'value' : admin_roles, 'Description' : 'Role users get when they are muted' } ,
        { 'name' : "muted_role",  'value' : muted_role, 'Description' : 'Role users get when they are muted' } ,
        { 'name' : "log_channel_id", 'value' : channel_id, 'Description': 'Channel where log results go' }])

    counts = settingcol.find({},{ "addresses": { "$slice": [0, 1] } ,'_id': 0})
    for key in counts:
        print(key)
    print(setting)

if __name__ == "__main__":
    mock_guild = type('Guild', (object,), {'name':'bot-test'})
    asyncio.run(set_defaults(mock_guild, 788119131068301335, admin_roles=802721665787887627, muted_role=802721664365232158))
