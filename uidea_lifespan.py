from libs import plugin
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_helper, ui_error
from addons.UIdea.libs.ui_constants import *
import time, discord

class Plugin(plugin.AdminPlugin, plugin.OnReadyPlugin):
    '''UIdea plugin to terminate UIs.
The lifespan of your UI should be declared in the config .json for it.

For more information about UIdea, see GitHub : <https://github.com/IdeaBot/UIdea>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong.

**NOTE:** This is run periodically and independently, so it could delete something mid-action in extreme cases '''

    def __init__(self, *args, always_watch_messages=list(), **kwargs):
        super().__init__(*args, always_watch_messages=always_watch_messages, **kwargs)
        self.always_watch_messages=always_watch_messages

    async def action(self):
        to_del = list()
        for ui in self.public_namespace.ui_messages:
            ui_inst_dict = self.public_namespace.ui_messages[ui]
            # get associated ui json
            ui_json = self.public_namespace.ui_jsons[self.public_namespace.ui_messages[ui][UI_NAME]]
            # compare ui json lifespan with ui_message timespan since last update
            if ui_json[LIFESPAN]>=0 and (time.time()-ui_inst_dict[LAST_UPDATED])>ui_json[LIFESPAN]:
                # if past lifespan
                # do onDelete
                if ui_json[ONDELETE]:
                    result, is_success = ui_helper.do_eval(ui_json[ONDELETE], self.public_namespace.ui_messages[ui], ui_json)
                # delete message
                try:
                    await self.bot.delete_message(ui_inst_dict[UI_INSTANCE].message)
                except discord.NotFound:
                    # if the message couldn't be found it rly should be deleted
                    pass
                # delete watch message entry
                msg_id, channel_id = ui.split(':')
                for msg in self.always_watch_messages:
                    if msg.id==msg_id and msg.channel.id==channel_id:
                        self.always_watch_messages.remove(msg)
                        break
                to_del.append(ui)
        # delete ui_instance data
        for i in to_del:
            # print("Deleting "+i) # debug
            del(self.public_namespace.ui_messages[i])
