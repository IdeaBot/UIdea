''' A collection of miscellaneous functions to simplify UIdea code

Created 2019-01-23 by NGnius '''

from addons.UIdea.libs import ui as ui_class
from addons.UIdea.libs.ui_constants import *
from addons.UIdea.libs import ui_error
import traceback

def do_eval(func_name, ui_message, ui_json, *args, **kwargs):
    try:
        return eval('ui_message[UI_INSTANCE]'+'.'+func_name+'(*args, **kwargs)'), True
    except Exception as e:
        # TODO : report error
        error_desc = 'Error in `%s` method for ui `%s`' %(func_name, ui_message[UI_NAME])
        #print(error_desc)
        #traceback.print_exc()
        ui_error.report_ui_error(e, ui_json, error_desc)
    return None, False
