from libs import embed

DEFAULT_EMBED_DICT = {'description':'placeholder UI'}

class UI:
    def __init__(self, loop, edit_msg, msg):
        self.loop = loop
        self.message = msg
        self.edit_message = edit_msg
        self.embed = makeEmbed()

    def update(self):
        # _update(self.message, self.getEmbed())
        # self.loop.call_soon(self._update, self.message, self.getEmbed())
        self.loop.create_task(self.edit_message(self.message, embed=self.getEmbed()))

    async def _update(self, msg, embed):
        await self.edit_message(msg, embed=embed)

    def getEmbed(self):
        return self.embed

def makeEmbed():
    return embed.create_embed(**DEFAULT_EMBED_DICT)
