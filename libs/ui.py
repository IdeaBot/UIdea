from libs import embed


class UI:
    def __init__(self, loop, edit_msg, msg):
        self.embed = makeEmbed(msg.embeds[0])

    def update(self):
        # _update(self.message, self.getEmbed())
        # self.loop.call_soon(self._update, self.message, self.getEmbed())
        self.loop.create_task(self.edit_message(self.message, embed=self.getEmbed()))

    async def _update(self, msg, embed):
        await self.edit_message(msg, embed=embed)

    def getEmbed(self):
        return self.embed


def makeEmbed(embed_dict):
    return embed.create_embed(**embed_dict)
