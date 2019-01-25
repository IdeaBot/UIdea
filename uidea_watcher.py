from libs import reaction
from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs import ui_helper, ui_error
from addons.UIdea.libs.ui_constants import *
import asyncio
import discord, time
import traceback

class Reaction(reaction.ReactionAddCommand, reaction.ReactionRemoveCommand):
    '''UIdea plugin to watch for reactions to UI messages.
This calls the function associated with the emoji, as defined in the .json config file for your ui.

For more information about UIdea, see it on GitHub : <https://github.com/IdeaBot/UIdea>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong. '''
    def __init__(self, *args, **kwargs):
        self.emoji=None
        super().__init__(*args, **kwargs)
        self.emoji=None

    def matches(self, reaction, user):
        if reaction.message.id+':'+reaction.message.channel.id in self.public_namespace.ui_messages and user.id != reaction.message.server.me.id:
            # print(reaction.emoji) # NOTE: certain emojis are converted to different emojis by discord; don't ask why
            # ui_inst_dict is the specific UI's instance variables
            ui_inst_dict = self.public_namespace.ui_messages[reaction.message.id+':'+reaction.message.channel.id]
            # ui_json is the specific UI's general variables (ie behaviour settings)
            ui_json = self.public_namespace.ui_jsons[ui_inst_dict[UI_NAME]]
            # ui instance must be active in order for reaction "buttons" to work
            if ui_inst_dict[IS_LIVE]:
                # get emoji, accounting for chr emojis and custom emojis (their ID is used)
                if isinstance(reaction.emoji, str):
                    emoji = reaction.emoji
                else:
                    emoji = reaction.emoji.id
                emoji_match = emoji in ui_json[ONREACTION]
                # print('Emoji matches:', emoji_match)
                if ui_json[PRIVATE]:
                    return user.id==ui_inst_dict[CREATOR] and emoji_match
                else:
                    return emoji_match
        # print('You\'re no match for me!')
        return False

    @asyncio.coroutine
    def action(self, reaction, user):
        ui_inst_dict = self.public_namespace.ui_messages[reaction.message.id+':'+reaction.message.channel.id]
        # update last update time
        ui_inst_dict[LAST_UPDATED] = time.time()
        # determine emoji type to use
        if isinstance(reaction.emoji, str):
            emoji = reaction.emoji
        else:
            emoji = reaction.emoji.id
        onReaction_func_name = self.public_namespace.ui_jsons[ui_inst_dict[UI_NAME]][ONREACTION][emoji]
        # print(onReaction_func_name)
        result, is_success = ui_helper.do_eval(onReaction_func_name, ui_inst_dict, self.public_namespace.ui_jsons[ui_inst_dict[UI_NAME]], reaction, user)
