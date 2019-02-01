from libs import testlib
from addons.UIdea.libs.ui_constants import *
from addons.UIdea.libs import ui_create
from addons.UIdea.libs import ui as ui_class

test_fail_messages = ['', ' ']


class StartTest(testlib.TestCase):
    def setUp(self):
        super().setUp()
        self.uidea_starter = self.bot.plugins['uidea_starter']

    def test_ui_match(self):
        for ui_name in self.uidea_starter.public_namespace.ui_jsons:
            for msg_content in test_fail_messages:
                msg = testlib.TestMessage(content=msg_content)
                sc = self.uidea_starter.public_namespace.ui_jsons[ui_name][SHOULDCREATE]
                is_match = eval('self.uidea_starter.public_namespace.uis[ui_name].UI.'+sc+'(msg)')
                self.assertFalse(is_match, 'UI "%s" matched blank message, which is not allowed' % (ui_name))
                self.assertEqual(msg.content, msg_content, 'UI "%s" match modified message' % (ui_name))

    def test_ui_init(self):
        for ui in self.uidea_starter.public_namespace.ui_jsons:
            ui_msg = testlib.TestMessage(content=' ', embed=ui_class.makeEmbed(self.uidea_starter.public_namespace.ui_jsons[ui][DEFAULT_EMBED]))
            ui_instance = ui_create.create_instance(self.uidea_starter.public_namespace.uis[ui], ui_msg, self.uidea_starter.public_namespace.ui_jsons[ui], self.bot.loop, self.bot.edit_message)
            self.assertIsNotNone(ui_instance, 'UI "%s" failed to init: see addons/UIdea/data/UIdea.log for more information' % (ui))
