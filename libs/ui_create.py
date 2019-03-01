''' Collection of functions for creating new UI instances

Created 2019-01-23 by NGnius '''

from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs.ui_constants import *
from addons.UIdea.libs import ui_error, ui_helper
from libs import loader
import time
import discord


def create_instance(ui_lib, ui_msg, ui_json, bot_loop, edit_msg):
    try:
        return ui_lib.UI(bot_loop, edit_msg, ui_msg)
    except Exception as e:
        error_desc = 'Error in `%s` method for ui `%s`' % ('__init__', ui_json[INFO][NAME])
        # print(error_desc)
        # traceback.print_exc()
        ui_error.report_ui_error(e, ui_json, error_desc)


async def make_ui_from_message(ui_lib, ui_json, msg, bot_inst):
    return await make_ui(ui_lib, ui_json, bot_inst, msg)

async def make_ui(ui_lib, ui_json, bot_inst, msg=None, *args, **kwargs):
    temp_dict = dict()
    if msg is None:
        if isinstance(kwargs['author'], str):  # want str
            author_id = kwargs['author']
        else:
            author_id = kwargs['author'].id
        if isinstance(kwargs['channel'], str):   # don't want str
            channel = discord.Object(id=kwargs['channel'])
        else:
            channel = kwargs['channel']
    else:
        author_id = msg.author.id
        channel = msg.channel
    temp_dict[CREATOR] = author_id
    temp_dict[CREATION_TIME] = temp_dict[LAST_UPDATED] = time.time()
    temp_dict[UI_NAME] = ui_json[INFO][NAME]
    temp_dict[IS_LIVE] = False
    ui_msg = await bot_inst.send_message(channel, embed=ui_class.makeEmbed(ui_json[DEFAULT_EMBED]) )
    temp_dict[ID]=ui_msg.id+':'+ui_msg.channel.id
    temp_dict[UI_INSTANCE] = create_instance(ui_lib, ui_msg, ui_json, bot_inst.loop, bot_inst.edit_message)
    if temp_dict[UI_INSTANCE] is None:
        await bot_inst.delete_message(ui_msg)
        return
    # assign attributes to UI instance
    try:
        # set public_namespace
        if ui_json[INFO][PACKAGE]:
            if ui_json[INFO][PACKAGE] not in loader.sub_namespaces:
                loader.sub_namespaces[ui_json[INFO][PACKAGE]] = loader.CustomNamespace()
            temp_dict[UI_INSTANCE].public_namespace = loader.sub_namespaces[ui_json[INFO][PACKAGE]]
        else:
            temp_dict[UI_INSTANCE].public_namespace = loader.namespace
        # NOTE: The following attributes should already be set up, this is just in case
        # set bot loop
        temp_dict[UI_INSTANCE].loop = bot_inst.loop
        # set message
        temp_dict[UI_INSTANCE].message = ui_msg
        # set edit_message func
        temp_dict[UI_INSTANCE].edit_message = bot_inst.edit_message
        # set embed
        temp_dict[UI_INSTANCE].embed = ui_class.makeEmbed(ui_msg.embeds[0])
        # set bot, if posesses permissions
        if ui_json[ACCESS_LEVEL] == 9:
            temp_dict[UI_INSTANCE].bot = temp_dict[UI_INSTANCE].client = bot_inst
    except Exception as e:
        # UI instance is probably in an invalid state wrt attributes right now;
        # abort instance
        error_desc = 'Error assigning attributes while creating ui `%s`' %(ui_json[INFO][NAME])
        ui_error.report_ui_error(e, ui_json, error_desc)
        await bot_inst.delete_message(ui_msg)
        return
    # add reactions to ui msg
    for emoji in ui_json[ONREACTION]:
        emoji = emoji.strip()
        if len(emoji) == 18:  # discord ID length is 18
            emoji = discord.Object(id=emoji)
        else:
            emoji = emoji[0]
            # TODO: Fix json on loading in cases where there are hidden characters
        await bot_inst.add_reaction(ui_msg, emoji)
    if ui_json[ONCREATE] is not None:
        result, is_success = ui_helper.do_eval(ui_json[ONCREATE], temp_dict, ui_json, msg, *args, **kwargs)
        if not is_success:
            await bot_inst.delete_message(ui_msg)
            return
    # add ui message to always_watch_messages
    bot_inst.always_watch_messages.add(ui_msg)
    return temp_dict
