from libs import plugin
import discord

class Plugin(plugin.OnReactionPlugin):
    '''UIdea plugin to watch for reactions to UI messages.
This calls the function associated with the emoji, as defined in the .json config file for your ui.

For more information about UIdea, see it on GitHub : <link>

Your interaction with this will probably never be evident.
If it is evident, I've probably done something wrong. '''

    async def action(self, reaction, user):
        if reaction.message.id+':'+reaction.message.channel.id in self.public_namespace.ui_messages \
         and self.public_namespace.ui_messages[reaction.message.id+':'+reaction.message.channel.id][self.public_namespace.IS_LIVE]:
            ui_dict = self.public_namespace.ui_messages
            # verify user and reaction are OK for interacting with UI instance
            # check if private; do nothing if is private and reactor and ui creator are not the same
            if self.public_namespace.ui_jsons[ui_dict[self.public_namespace.UI_NAME]][self.public_namespace.INFO][self.public_namespace.PRIVATE] \
             and user.id!=ui_dict[CREATOR]:
                return
            if isinstance(reaction.emoji, str):
                emoji = reaction.emoji
            else:
                emoji = reaction.emoji.id
            if emoji not in self.public_namespace.ui_jsons[self.public_namespace.ONREACTION]:
                return
            onReaction_func_name = self.public_namespace.ui_jsons[ui_dict[self.public_namespace.UI_NAME]][self.public_namespace.REACTION][emoji]
            eval('ui_dict[self.public_namespace.UI_INSTANCE].'+onReaction_func_name+'(reaction, user)')
