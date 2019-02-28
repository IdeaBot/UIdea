'''A collection of constants used across UIdea
This also makes sure the file structure implied by some constants exists

Created 2019-01-23 by NGnius '''
import os
from libs import dataloader

DISCORD_RXN_MAX = 20

UI_DATA_PATH = 'addons/UIdea/data'
DEFAULT_UIDEA_JSON = 'default_uidea_json.json'

DEFAULT_JSON = dataloader.datafile(os.path.join(UI_DATA_PATH, DEFAULT_UIDEA_JSON), load_as='json').content
if not os.path.isdir(UI_DATA_PATH):
    os.mkdir(UI_DATA_PATH)
UI_JSONS_PATH = 'addons'
# print(json.dumps(DEFAULT_JSON, indent=4)) # debug
UI_SAVE_LOC = os.path.join(UI_DATA_PATH, 'saved')
if not os.path.isdir(UI_SAVE_LOC):
    os.mkdir(UI_SAVE_LOC)

UI_PICKLE_LOC = os.path.join(UI_DATA_PATH, 'pickles')
if not os.path.isdir(UI_PICKLE_LOC):
    os.mkdir(UI_PICKLE_LOC)

SUPPORTED_API_VERSIONS = [
                        'v0.0.1',  # >> current
                        'v0.0.2',  #
                        'v0.0.3',  #
                        'v0.0.4'   #
                        ]

# constants for json file
VERSION = 'version'
API = 'api'
TYPE = 'type'

INFO = 'info'
NAME = 'name'
DESCRIPTION = 'description'
HELP = 'help'
PACKAGE = 'package'
FILEPATH = 'filepath'
OWNER = 'owner'
MAINTAINERS = 'maintainers'

LIFESPAN = 'lifespan'
PERSISTENCE = 'persistence'
PRIVATE = 'private'
ACCESS_LEVEL = 'accessLevel'
DIRECT_ONLY = 'directOnly'
SHOULDCREATE = 'shouldCreate'
ONCREATE = 'onCreate'
ONDELETE = 'onDelete'
ONPERSIST = 'onPersist'
ONREACTION = 'onReaction'
ONMESSAGE = 'onMessage'
DEFAULT_EMBED = 'defaultEmbed'
DEBUG = 'debug'

# ui_messages constants
UI_INSTANCE = 'UI Instance'
CREATOR = 'creator'
CREATION_TIME = 'creation time'
LAST_UPDATED = 'last updated'
UI_NAME = 'UI Name'
IS_LIVE = 'isLive'
ID = 'Id'
