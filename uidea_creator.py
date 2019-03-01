from libs import plugin, dataloader, loader
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_create, ui_error
from addons.UIdea.libs.ui_constants import *

class Plugin(plugin.AdminPlugin):
    def on_client_add(self):
        ui_create.create_ui = self.create_ui

    def create_ui(self, name, message=None, *args, **kwargs):
        ui_lib = self.public_namespace.uis[name]
        ui_json = self.public_namespace.ui_jsons[name]
        ui_task = self.assemble_ui(ui_lib, ui_json, self.bot, msg=message, *args, **kwargs)
        self.bot.loop.create_task(ui_task)

    async def assemble_ui(self, *args, **kwargs):
        temp_dict = await ui_create.make_ui(*args, **kwargs)
        if temp_dict is not None:  # if no error during creation
            self.public_namespace.ui_messages[temp_dict[ID]]=temp_dict
            self.public_namespace.ui_messages[temp_dict[ID]][IS_LIVE]=True
