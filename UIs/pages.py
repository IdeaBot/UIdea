from addons.UIdea.libs import ui as ui_class

BOOK = ['Once upon a time, a while ago, stuff happened', 'I think they made a movie about it, but I don\'t remember', 'Anyway, it was a cool story, you should go see it. THE END']
BOOK_TITLE = 'A Story'

class UI(ui_class.UI):
    '''Example and test implementation of UI'''

    def shouldCreate(message):
        return 'read' in message.content.lower()

    def onCreate(self, msg):
        self.page=0
        self.page_list = BOOK
        self.embed.title = BOOK_TITLE
        self.update_embed()

    def onRight(self, reaction, user):
        if self.page<len(self.page_list):
            self.page+=1
            self.update_embed()

    def onLeft(self, reaction, user):
        if self.page>0:
            self.page-=1
            self.update_embed()

    def update_embed(self):
        self.embed.description=self.page_list[self.page]
        self.embed.set_footer(text='Page '+str(self.page))
        self.update()
