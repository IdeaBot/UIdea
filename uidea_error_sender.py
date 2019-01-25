from addons.UIdea.libs import ui_error
from libs import plugin
import discord

class Plugin(plugin.ThreadedPlugin, plugin.OnReadyPlugin, plugin.AdminPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.queue=ui_error.error_messages_q

    async def action(self):
        while not ui_error.error_messages_q.empty():
            action_dict = ui_error.error_messages_q.get()
            for key in action_dict:
                if plugin.ARGS in action_dict[key]:
                    for arg in list(action_dict[key][plugin.ARGS]):
                        if isinstance(arg, str) and len(arg)==18:
                            # is user id; convert to discord user object
                            user = discord.utils.find(lambda u: u.id == arg, self.bot.get_all_members())
                            if user is not None:
                                index = action_dict[key][plugin.ARGS].index(arg)
                                action_dict[key][plugin.ARGS].remove(arg)
                                action_dict[key][plugin.ARGS].insert(index, user)
                            else:
                                ui_error.report_issue('Unable to find user with ID %s'%arg)
            self.queue.put(action_dict)
        await super().action()
