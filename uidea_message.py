from libs import plugin
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_helper, ui_error
from addons.UIdea.libs.ui_constants import *
import time

class Plugin(plugin.OnMessagePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.me = None
    async def action(self, msg):
        if msg.server is not None:
            self.me = msg.server.me
        if msg.author != self.me:
            for ui_id in self.public_namespace.ui_messages:
                if self.public_namespace.ui_messages[ui_id][IS_LIVE]:
                    _, ui_channel_id = ui_id.split(':')
                    if ui_channel_id == msg.channel.id:
                        ui_msg = self.public_namespace.ui_messages[ui_id]
                        ui_json = self.public_namespace.ui_jsons[ui_msg[UI_NAME]]
                        if ui_json[ONMESSAGE] is not None:
                            _, success = ui_helper.do_eval(ui_json[ONMESSAGE], ui_msg, ui_json, msg)
                            if success:
                                ui_msg[LAST_UPDATED] = time.time()
