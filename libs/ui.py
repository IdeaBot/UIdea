from libs import embed

DEFAULT_EMBED_DICT = {'description':'placeholder UI'}

class UI:
    def __init__(self, loop, edit_msg, msg):
        self.loop = loop
        self.message = msg
        self.edit_message = edit_msg
        self.embed = makeEmbed()

    def update(self):
        self.loop.run_until_complete(self.edit_message(self.message, embed=self.getEmbed()))

    def getEmbed(self):
        return self.embed

def makeEmbed():
    return embed.create_embed(**DEFAULT_EMBED_DICT)
