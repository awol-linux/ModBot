from pymongo import MongoClient
import os
import asyncio

PASS = os.getenv('MONGO_PASSWORD')
USER = os.getenv('MONGO_USER')

# Create connection to MongoDB
client = MongoClient('mongodb', 27017 , username=USER, password=PASS)

botdb = client['ModBot']
async def set_defaults(guild, channel_id="", admin_roles='', muted_role=""):
    guildname = str(guild.name).lower()
    namesafe = ''.join(e for e in guildname if e.isalnum())
    guildid = str(guild.id)
    settingcol = botdb['settingdb-' + namesafe + guildid[-4]]

    # Clear settings

    settingcol.drop()

    # Insert the settings into Mongo

    settingcol.insert_many([
        { 'name' : "prefix", 'value' : "./", 'Description' : 'Sets the command prefix' }, 
        { 'name' : "admin_roles",  'value' : admin_roles, 'Description' : 'A user needs a role in this list to run commands (assuming they don\'t have discord Administrator perms)' } ,
        { 'name' : "muted_role",  'value' : muted_role, 'Description' : 'A user gets this role when they are muted' } ,
        { 'name' : "log_channel_id", 'value' : channel_id, 'Description': 'The default log channel. Unless an action item has a channel set, the bot will log those action items to this channel.' }])

    counts = settingcol.find({},{ "addresses": { "$slice": [0, 1] } ,'_id': 0})
    for key in counts:
        print(key)
    print(settingcol)
async def set_action_items():
    data = [
            { 'name' : 'Toggled_Mute', 'prettys': ['Muted', 'Unmuted'] },
            { 'name' : 'Toggled_Role', 'prettys': ['Gave Role', 'Removed Role']},
            { 'name' : 'Toggled_VC_Mute', 'prettys': ['VC Muted', 'VC Unmute']},
            { 'name' : 'Toggled_VC_deaf', 'prettys': ['VC deafened', 'VC undeafened']},
            { 'name' : 'Banned', 'prettys': ['Banned']},
            { 'name' : 'Unbanned', 'prettys': ['unbanned']}
        ]
    action_item_coll = botdb['action_items']
    action_item_coll.insert_many(data)

if __name__ == "__main__":
#    mock_guild = type('Guild', (object,), {'name':'bot-test'})
    # asyncio.run(set_defaults(mock_guild, 788119131068301335, admin_roles=802721665787887627, muted_role=802721664365232158))
    asyncio.run(set_action_items())
