from libs import plugin
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_helper, ui_error
from addons.UIdea.libs.ui_constants import *

class Plugin(plugin.OnMessagePlugin):
    async def action(self, msg):
        for ui_id in self.public_namespace.ui_messages:
            _, ui_channel_id = ui_id.split(':')
            if ui_channel_id == msg.channel.id:
                ui_msg = self.public_namespace.ui_messages[ui_id]
                ui_json = self.public_namespace.ui_jsons[ui_msg[UI_NAME]]
                if ui_json[ONMESSAGE] is not None:
                    ui_helper.do_eval(ui_json[ONMESSAGE], ui_message, ui_json, msg)
