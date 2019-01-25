from libs import plugin, dataloader
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_create, ui_error
from addons.UIdea.libs.ui_constants import *
import os, json, time
import discord
import re
import traceback
import pickle

class Plugin(plugin.AdminPlugin, plugin.OnMessagePlugin):
    '''UIdea plugin to create new UIs.
Conditions for creating a new UI message should be defined in the .json config file for your ui.

For more information about UIdea, see GitHub : <https://github.com/IdeaBot/UIdea>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong. '''
    def on_client_add(self):
        # true startup
        # load ui jsons
        self.public_namespace.ui_jsons = load_ui_jsons(UI_JSONS_PATH)
        # load each ui as defined in each json
        self.public_namespace.uis = load_uis(self.public_namespace.ui_jsons)
        #print("UI JSON")
        #print(json.dumps(self.public_namespace.ui_jsons, indent=4))
        self.public_namespace.ui_messages = self.load_ui_messages(self.public_namespace.ui_jsons) # load for persistence


    async def action(self, msg):
        # ignore private messages, for now
        if not msg.server:
            return
        for ui in self.public_namespace.uis:
            try:
                is_match = eval('self.public_namespace.uis[ui].UI.'+self.public_namespace.ui_jsons[ui][SHOULDCREATE]+'(msg)')
            except Exception as e:
                # TODO: system to notify owner of shouldCreate startup error
                error_desc = 'Error in `%s` method for ui `%s`' %(self.public_namespace.ui_jsons[ui][SHOULDCREATE], ui)
                #print(error_desc)
                #traceback.print_exc()
                ui_error.report_ui_error(e, self.public_namespace.ui_jsons[ui], error_desc)
            else:
                if is_match:
                    temp_dict = await ui_create.make_ui(self.public_namespace.uis[ui], self.public_namespace.ui_jsons[ui], msg, self.bot)
                    if temp_dict is not None:
                        self.public_namespace.ui_messages[temp_dict[ID]]=temp_dict
                        self.public_namespace.ui_messages[temp_dict[ID]][IS_LIVE]=True
                    break

    def shutdown(self):
        self.save_ui_messages(self.public_namespace.ui_messages)

    def save_ui_messages(self, ui_messages):
        # clear save folder
        for f in os.listdir(UI_SAVE_LOC):
            try:
                os.remove(os.path.join(UI_SAVE_LOC, f))
            except OSError as e:
                # TODO: proper logging for errors
                error_desc = 'Error deleting %s' %(os.path.join(UI_SAVE_LOC, f))
                #print(error_desc)
                #traceback.print_exc()
                #pass
                ui_error.report_error(e, error_desc, user=None)
        # clear pickle folder
        for f in os.listdir(UI_PICKLE_LOC):
            try:
                os.remove(os.path.join(UI_PICKLE_LOC, f))
            except OSError as e:
                # TODO: proper logging for errors
                error_desc = 'Error deleting %s' %(os.path.join(UI_PICKLE_LOC, f))
                #print(error_desc)
                #traceback.print_exc()
                #pass
                ui_error.report_error(e, error_desc, user=None)

        for ui in ui_messages:
            if self.public_namespace.ui_jsons[ui_messages[ui][UI_NAME]][PERSISTENCE]:
                # print('Now saving', ui_messages[ui][UI_NAME]) # debug
                # print(ui_messages[ui][UI_INSTANCE].__dict__) # debug
                pickle_loc = os.path.join(UI_PICKLE_LOC, ui)
                ui_message_json_loc = os.path.join(UI_SAVE_LOC, ui+'.json')
                # delete incompatible vars
                del(ui_messages[ui][UI_INSTANCE].edit_message)
                del(ui_messages[ui][UI_INSTANCE].loop)
                # picke ui instance and save
                with open(pickle_loc, 'wb') as file:
                    pickle.dump(ui_messages[ui][UI_INSTANCE], file, protocol=pickle.HIGHEST_PROTOCOL)
                # replace ui_instance value with filepath
                ui_dict = dict(ui_messages[ui]) # copy
                ui_dict[UI_INSTANCE]=pickle_loc
                # save json
                with open(ui_message_json_loc, 'w') as file:
                    json.dump(ui_dict, file)

    def load_ui_messages(self, ui_jsons):
        result = dict()
        for f in os.listdir(UI_SAVE_LOC):
            if os.path.isfile(os.path.join(UI_SAVE_LOC, f)) and f.endswith('.json'):
                key = f[:-len('.json')]
                # load json
                with open(os.path.join(UI_SAVE_LOC, f), 'r') as file:
                    result[key]=json.load(file)
                # print('Reloading', result[key][UI_NAME]) # debug
                # load pickle into ui_instance
                with open(result[key][UI_INSTANCE], 'rb') as file:
                    result[key][UI_INSTANCE]=pickle.load(file)
                # update LAST_UPDATED
                result[key][LAST_UPDATED]=time.time()
                if result[key][UI_NAME] not in ui_jsons:
                    del(result[key])
                else:
                    # restore incompatible vars
                    result[key][UI_INSTANCE].loop = self.bot.loop
                    result[key][UI_INSTANCE].edit_message = self.edit_message
                    if ui_jsons[result[key][UI_NAME]][ONPERSIST]:
                        try:
                            eval('result[key][UI_INSTANCE].'+ui_jsons[result[key][UI_NAME]][ONPERSIST]+'()')
                        except Exception as e:
                            # TODO: system to notify owner of startup error
                            error_desc = 'Error in `%s` method for ui `%s`' %(ui_jsons[result[key][UI_NAME]][ONPERSIST], result[key][UI_NAME])
                            #print(error_desc)
                            #traceback.print_exc()
                            ui_error.report_ui_error(e, ui_jsons[result[key][UI_NAME]], error_desc)
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
                    desc = '!!! Error in JSON of ui %s' %(f[:-len('.json')])
                    # print(error_desc)
                    ui_error.report_issue(desc)
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
                            desc = '!!! Error in JSON of ui %s' %(sub_f[:-len('.json')])
                            # print(error_desc)
                            ui_error.report_issue(desc)
    # print('Loaded JSONS:', ui_jsons) # debug
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
