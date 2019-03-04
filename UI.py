from libs import command
from addons.UIdea.libs.ui_constants import *

class Command(command.Dummy):
    ''' User Interfaces are fun. This is mainly a helping command
**Usage**
To get a list of available UIs
```@Idea help UI list ```

To get help with a specific UI
```@Idea help UI <ui> ```
Where
**`<ui>`** is the ui you want help with'''
    def help(self, help_msg, *args, **kwargs):
        if help_msg:
            help_arg = help_msg.strip()
            if help_arg.lower() == 'list':
                return self.ui_list()
            if help_arg and help_arg in self.public_namespace.ui_jsons:
                return self.public_namespace.ui_jsons[help_arg][INFO][DESCRIPTION] + '\n\n' + self.public_namespace.ui_jsons[help_arg][INFO][HELP]
            else:
                return 'The requested UI `%s` could not be found\n'%help_msg+super().help(help_msg, *args, **kwargs)
        else:
            return super().help(help_msg, *args, **kwargs)

    def ui_list(self):
        return '**NOTE:** Names are case sensitive\n\n__Available UI List__\n'+'\n'.join(self.public_namespace.ui_jsons.keys())
