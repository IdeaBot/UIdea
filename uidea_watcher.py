from libs import reaction
import asyncio
import discord
import traceback

class Reaction(reaction.ReactionAddCommand, reaction.ReactionRemoveCommand):
    '''UIdea plugin to watch for reactions to UI messages.
This calls the function associated with the emoji, as defined in the .json config file for your ui.

For more information about UIdea, see it on GitHub : <link>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong. '''
    def __init__(self, *args, **kwargs):
        self.emoji=None
        super().__init__(*args, **kwargs)
        self.emoji=None

    def matches(self, reaction, user):
        if reaction.message.id+':'+reaction.message.channel.id in self.public_namespace.ui_messages and user.id != reaction.message.server.me.id:
            # ui_inst_dict is the specific UI's instance variables
            ui_inst_dict = self.public_namespace.ui_messages[reaction.message.id+':'+reaction.message.channel.id]
            # ui_json is the specific UI's general variables (ie behaviour settings)
            ui_json = self.public_namespace.ui_jsons[ui_inst_dict[self.public_namespace.UI_NAME]]
            # ui instance must be active in order for reaction "buttons" to work
            if ui_inst_dict[self.public_namespace.IS_LIVE]:
                # get emoji, accounting for chr emojis and custom emojis (their ID is used)
                if isinstance(reaction.emoji, str):
                    emoji = reaction.emoji
                else:
                    emoji = reaction.emoji.id
                emoji_match = emoji in ui_json[self.public_namespace.ONREACTION]
                print('Emoji matches:', emoji_match)
                if ui_json[self.public_namespace.PRIVATE]:
                    return user.id==ui_inst_dict[self.public_namespace.CREATOR] and emoji_match
                else:
                    return emoji_match
        print('You\'re no match for me!')
        return False

    @asyncio.coroutine
    def action(self, reaction, user):
        ui_inst_dict = self.public_namespace.ui_messages[reaction.message.id+':'+reaction.message.channel.id]
        if isinstance(reaction.emoji, str):
            emoji = reaction.emoji
        else:
            emoji = reaction.emoji.id
        onReaction_func_name = self.public_namespace.ui_jsons[ui_inst_dict[self.public_namespace.UI_NAME]][self.public_namespace.ONREACTION][emoji]
        try:
            eval('ui_inst_dict[self.public_namespace.UI_INSTANCE].'+onReaction_func_name+'(reaction, user)')
        except:
            # TODO: notify UI owner of failure
            traceback.print_exc()
            pass
