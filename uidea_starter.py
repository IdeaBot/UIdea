from libs import plugin, dataloader
from addons.UIdea.libs import ui as ui_class
import os, json, time
import discord
import re
import traceback

DISCORD_RXN_MAX = 20

UI_DATA_PATH = 'addons/UIdea/data'
DEFAULT_UIDEA_JSON = 'default_uidea_json.json'

DEFAULT_JSON = dataloader.datafile(os.path.join(UI_DATA_PATH, DEFAULT_UIDEA_JSON), load_as='json').content
UI_JSONS_PATH = 'addons'
# print(json.dumps(DEFAULT_JSON, indent=4)) # debug
UI_SAVE_LOC = os.path.join(UI_DATA_PATH, 'saved')
if not os.path.isdir(UI_SAVE_LOC):
    os.mkdir(UI_SAVE_LOC)

SUPPORTED_API_VERSIONS = ['v0.0.1', 'v0.0.2', 'v0.0.3', 'v0.0.4']

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
SHOULDCREATE = 'shouldCreate'
ONCREATE = 'onCreate'
ONDELETE = 'onDelete'
ONPERSIST = 'onPersist'
ONREACTION = 'onReaction'
DEBUG = 'debug'

# ui_messages constants
UI_INSTANCE = 'UI Instance'
CREATOR = 'creator'
CREATION_TIME = 'creation time'
LAST_UPDATED = 'last updated'
UI_NAME = 'UI Name'
IS_LIVE = 'isLive'

class Plugin(plugin.AdminPlugin, plugin.OnMessagePlugin):
    '''UIdea plugin to create new UIs.
Conditions for creating a new UI message should be defined in the .json config file for your ui.

For more information about UIdea, see GitHub : <https://github.com/IdeaBot/UIdea>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong. '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # transfer contants to public namespace
        self.public_namespace.UI_DATA_PATH = UI_DATA_PATH

        # constants for json file
        self.public_namespace.VERSION = VERSION
        self.public_namespace.API = API
        self.public_namespace.TYPE = TYPE

        self.public_namespace.INFO = INFO
        self.public_namespace.NAME = NAME
        self.public_namespace.DESCRIPTION = DESCRIPTION
        self.public_namespace.HELP = HELP
        self.public_namespace.PACKAGE = PACKAGE
        self.public_namespace.FILEPATH = FILEPATH
        self.public_namespace.OWNER = OWNER
        self.public_namespace.MAINTAINERS = MAINTAINERS

        self.public_namespace.LIFESPAN = LIFESPAN
        self.public_namespace.PERSISTENCE = PERSISTENCE
        self.public_namespace.PRIVATE = PRIVATE
        self.public_namespace.SHOULDCREATE = SHOULDCREATE
        self.public_namespace.ONCREATE = ONCREATE
        self.public_namespace.ONDELETE = ONDELETE
        self.public_namespace.ONPERSIST = ONPERSIST
        self.public_namespace.ONREACTION = ONREACTION
        self.public_namespace.DEBUG = DEBUG

        # ui_messages constants
        self.public_namespace.UI_INSTANCE = UI_INSTANCE
        self.public_namespace.CREATOR = CREATOR
        self.public_namespace.CREATION_TIME = CREATION_TIME
        self.public_namespace.LAST_UPDATED = LAST_UPDATED
        self.public_namespace.UI_NAME = UI_NAME
        self.public_namespace.IS_LIVE = IS_LIVE


    def on_client_add(self):
        # true startup
        if not os.path.isdir(UI_DATA_PATH):
            os.mkdir(UI_DATA_PATH)
        # load ui jsons
        self.public_namespace.ui_jsons = load_ui_jsons(UI_JSONS_PATH)
        # load each ui as defined in each json
        self.public_namespace.uis = load_uis(self.public_namespace.ui_jsons)
        #print("UI JSON")
        #print(json.dumps(self.public_namespace.ui_jsons, indent=4))
        self.public_namespace.ui_messages = self.load_ui_messages(self.public_namespace.ui_jsons) # load for persistence


    async def action(self, msg):
        for ui in self.public_namespace.uis:
            try:
                is_match = eval('self.public_namespace.uis[ui].UI.'+self.public_namespace.ui_jsons[ui][SHOULDCREATE]+'(msg)')
            except:
                # TODO: system to notify owner of shouldCreate startup error
                print('!!! Error in %s method for ui %s:' %(self.public_namespace.ui_jsons[ui][SHOULDCREATE], ui))
                traceback.print_exc()
                pass
            else:
                if is_match:
                    # ui_msg = await self.send_message(msg.channel, embed=temp_dict[UI_INSTANCE])
                    temp_dict = dict()
                    temp_dict[CREATOR] = msg.author.id
                    temp_dict[CREATION_TIME] = temp_dict[LAST_UPDATED] = time.time()
                    temp_dict[UI_NAME] = ui
                    temp_dict[IS_LIVE] = False
                    ui_msg = await self.send_message(msg.channel, embed=ui_class.makeEmbed())
                    try:
                        temp_dict[UI_INSTANCE] = self.public_namespace.uis[ui].UI(self.bot.loop, self.edit_message, ui_msg)
                    except:
                        # TODO: system to notify owner of startup error
                        print('!!! Error in %s method for ui %s:' %('__init__', ui))
                        traceback.print_exc()
                        pass
                    # add reactions to ui msg
                    for emoji in self.public_namespace.ui_jsons[ui][ONREACTION]:
                        emoji = emoji.strip()
                        if len(emoji)==18: # discord ID length is 18
                            emoji = discord.Object(id=emoji)
                        else:
                            emoji = emoji[0]
                            # TODO: Fix json on loading in cases where there are hidden characters
                        await self.add_reaction(ui_msg, emoji)
                    if self.public_namespace.ui_jsons[ui][ONCREATE] is not None:
                        try:
                            eval('temp_dict[UI_INSTANCE].'+self.public_namespace.ui_jsons[ui][ONCREATE]+'(msg)')
                        except:
                            # TODO: system to notify owner of startup error
                            print('!!! Error in %s method for ui %s:' %(self.public_namespace.ui_jsons[ui][ONCREATE], ui))
                            traceback.print_exc()
                            pass
                    self.public_namespace.ui_messages[ui_msg.id+':'+ui_msg.channel.id]=temp_dict
                    self.public_namespace.ui_messages[ui_msg.id+':'+ui_msg.channel.id][IS_LIVE]=True
                    break

    def shutdown(self):
        self.save_ui_messages(self.public_namespace.ui_messages)

    def save_ui_messages(self, ui_messages):
        for ui in ui_messages:
            # picke every ui instance and save
            # replace ui_instance value with filepath
            # save every json
            pass

    def load_ui_messages(self, ui_jsons):
        result = dict()
        for f in os.listdir(UI_SAVE_LOC):
            # load every json
            # load pickle into ui_instance
            pass
        return result



def load_ui_jsons(root):
    '''Search for & load ui jsons, up to two folders deep'''
    ui_jsons = dict()
    for f in sorted(os.listdir(root)):
        if os.path.isfile(os.path.join(root, f)):
            if f[-len('.json'):]=='.json' and f[0]!='_' and f!=DEFAULT_UIDEA_JSON:
                with open(os.path.join(root, f), 'r') as file:
                    temp_json = json.load(file)
                is_good = verify_ui_json(temp_json)
                if is_good:
                    merge_defaults(temp_json, package=None, name=f[:-len('.json')], filepath=os.path.join(root, f)[:-len('.json')])
                    correct_func_strs(temp_json)
                    ui_jsons[temp_json[INFO][NAME]]=temp_json
                else:
                    # TODO: log warning about invalid JSON
                    print('!!! Error in JSON of ui %s:' %(f[:-len('.json')]))
                    pass
        else:
            for sub_f in sorted(os.listdir(os.path.join(root, f))):
                if os.path.isfile(os.path.join(root, f, sub_f)):
                    if sub_f[-len('.json'):]=='.json' and sub_f[0]!='_':
                        with open(os.path.join(root, f, sub_f), 'r') as file:
                            temp_json = json.load(file)
                        is_good = verify_ui_json(temp_json)
                        if is_good:
                            merge_defaults(temp_json, package=f, name=sub_f[:-len('.json')], filepath=os.path.join(root, f, sub_f)[:-len('.json')])
                            correct_func_strs(temp_json)
                            ui_jsons[temp_json[INFO][NAME]]=temp_json
                        else:
                            # TODO: log warning about invalid JSON
                            print('!!! Error in JSON of ui %s:' %(sub_f[:-len('.json')]))
                            pass
    print('Loaded JSONS:', ui_jsons)
    return ui_jsons

def load_uis(ui_jsons):
    import importlib
    uis = dict()
    for ui in ui_jsons:
        try:
            import_path = ui_jsons[ui][INFO][FILEPATH]
            if import_path.endswith('.py'):
                import_path=import_path[:-len('.py')]
            elif import_path.endswith('.py/'):
                import_path=import_path[:-len('.py/')]
            import_path = re.sub(r'[\\\/]+', '.',import_path)
            ui_lib = importlib.import_module(import_path) # import ui python file
            uis[ui]=ui_lib
        except ImportError:
            traceback.print_exc()
            pass
    return uis


def verify_ui_json(json_var):
    if not isinstance(json_var, dict):
        return False
    # verify version info
    if VERSION in json_var and isinstance(json_var[VERSION], dict):
        if not (TYPE in json_var[VERSION] and API in json_var[VERSION]):
            return False
        if json_var[VERSION][API] not in SUPPORTED_API_VERSIONS:
            return False
    else:
        return False
    # verify reactions
    if ONREACTION in json_var:
        # check for correct type
        if not isinstance(json_var[ONREACTION], dict):
            return False
        # check that reactions does not exceed 20 (discord rxn limit)
        if len(json_var[ONREACTION])>DISCORD_RXN_MAX:
            return False
        # check that each emoji is of length 1 or 18 (ID length)
        for emoji in json_var[ONREACTION]:
            if len(emoji)!=1 and len(emoji)!=18:
                return False
    return True

def merge_defaults(json_dict, **kwargs):
    # merge default json into json_dict
    _merge_dict_r(DEFAULT_JSON, json_dict)
    # setup info's dynamic defaults
    for key in kwargs:
        if key in json_dict[INFO] and json_dict[INFO][key] is None and kwargs[key] is not None:
            json_dict[INFO][key]=kwargs[key]

def _merge_dict_r(merger, mergee):
    '''Merges the contents of merger into mergee
    Recurses if the same element of merger and mergee is a dict'''
    for key in merger:
        if key not in mergee:
            mergee[key]=merger[key]
        elif isinstance(mergee[key], dict) and isinstance(merger[key], dict):
            _merge_dict_r(merger[key], mergee[key])

def correct_func_strs(json_dict):
    '''Removes disallowed function names
    (eg names which involve calling another method will be replaced with something probably invalid
    but less risky when eventually executed with eval() ) '''
    for key in json_dict:
        if isinstance(json_dict[key], str):
            json_dict[key]=json_dict[key].strip().split()[0].strip(':;,')
            json_dict[key]=re.sub(r'\(.+\)?', '', json_dict[key], re.I)
    for key in json_dict[ONREACTION]:
        if isinstance(json_dict[ONREACTION][key], str):
            json_dict[ONREACTION][key]=json_dict[ONREACTION][key].strip().split()[0].strip(':;,')
            json_dict[ONREACTION][key]=re.sub(r'\(.+\)?', '', json_dict[ONREACTION][key], re.I)
