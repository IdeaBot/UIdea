from libs import command
import asyncio
from addons.UIdea.libs.ui_constants import *

class Command(command.DirectOnlyCommand):
    ''' Stop Idea from responding to the mention when a mention-only UI is used
This is necessary since uidea_starter is a Plugin, not a command, so no command will run until zz_invalid'''
    def matches(self, msg):
        for ui in self.public_namespace.uis:
            if self.public_namespace.ui_jsons[ui][DIRECT_ONLY]:
                try:
                    is_match = eval('self.public_namespace.uis[ui].UI.'+self.public_namespace.ui_jsons[ui][SHOULDCREATE]+'(msg)')
                except Exception as e:
                    traceback.print_exc()
                    pass # error will already be reported by uidea_starter
                else:
                    if is_match:
                        return True
        return False

    @asyncio.coroutine
    def action(self, msg):
        return
