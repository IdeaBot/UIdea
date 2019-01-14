from libs import plugin
import time

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
        print("Starting cleanup...")
        to_del = list()
        for ui in self.public_namespace.ui_messages:
            ui_inst_dict = self.public_namespace.ui_messages[ui]
            # get associated ui json
            ui_json = self.public_namespace.ui_jsons[self.public_namespace.ui_messages[ui][self.public_namespace.UI_NAME]]
            # compare ui json lifespan with ui_message timespan since last update
            if ui_json[self.public_namespace.LIFESPAN]>=0 and (time.time()-ui_inst_dict[self.public_namespace.LAST_UPDATED])>ui_json[self.public_namespace.LIFESPAN]:
                # if past lifespan
                # delete message
                # await self.edit_message(ui_inst_dict[self.public_namespace.UI_INSTANCE].message, new_content='Expired', embed=None)
                await self.bot.delete_message(ui_inst_dict[self.public_namespace.UI_INSTANCE].message)
                # TODO: actually delete message
                # delete watch message entry
                msg_id, channel_id = ui.split(':')
                for i in range(len(self.always_watch_messages)):
                    msg = self.always_watch_messages[i]
                    if msg.id==msg_id and msg.channel.id==channel_id:
                        del(self.always_watch_messages[i])
                to_del.append(ui)
        # delete ui_instance data
        for i in to_del:
            print("Deleting "+i)
            del(self.public_namespace.ui_messages[i])
        print(self.public_namespace.ui_messages)
