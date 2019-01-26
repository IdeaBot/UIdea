''' Collection of functions for creating new UI instances

Created 2019-01-23 by NGnius '''
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs.ui_constants import *
from addons.UIdea.libs import ui_error, ui_helper
import time

def create_instance(ui_lib, ui_msg, ui_json, bot_loop, edit_msg):
    try:
        return ui_lib.UI(bot_loop, edit_msg, ui_msg)
    except Exception as e:
        # TODO: system to notify owner of startup error
        error_desc = 'Error in `%s` method for ui `%s`' %('__init__', ui_json[INFO][NAME])
        #print(error_desc)
        #traceback.print_exc()
        ui_error.report_ui_error(e, ui_json, error_desc)

async def make_ui(ui_lib, ui_json, msg, bot_inst):
    temp_dict = dict()
    temp_dict[CREATOR] = msg.author.id
    temp_dict[CREATION_TIME] = temp_dict[LAST_UPDATED] = time.time()
    temp_dict[UI_NAME] = ui_json[INFO][NAME]
    temp_dict[IS_LIVE] = False
    ui_msg = await bot_inst.send_message(msg.channel, embed=ui_class.makeEmbed(ui_json[DEFAULT_EMBED]) )
    temp_dict[ID]=ui_msg.id+':'+ui_msg.channel.id
    temp_dict[UI_INSTANCE] = create_instance(ui_lib, ui_msg, ui_json, bot_inst.loop, bot_inst.edit_message)
    if temp_dict[UI_INSTANCE] is None:
        await bot_inst.delete_message(ui_msg)
        return
    # add reactions to ui msg
    for emoji in ui_json[ONREACTION]:
        emoji = emoji.strip()
        if len(emoji)==18: # discord ID length is 18
            emoji = discord.Object(id=emoji)
        else:
            emoji = emoji[0]
            # TODO: Fix json on loading in cases where there are hidden characters
        await bot_inst.add_reaction(ui_msg, emoji)
    if ui_json[ONCREATE] is not None:
        result, is_success = ui_helper.do_eval(ui_json[ONCREATE], temp_dict, ui_json, msg)
        if not is_success:
            await bot_inst.delete_message(ui_msg)
            return
    # add ui message to always_watch_messages
    bot_inst.always_watch_messages.add(ui_msg)
    return temp_dict