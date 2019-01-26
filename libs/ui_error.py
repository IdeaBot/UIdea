'''A collection of functions to make UI errors easier to handle and report

Created 2019-01-23 by NGnius '''

from addons.UIdea.libs.ui_constants import *
from libs import plugin, embed
import traceback, logging
from multiprocessing import Queue
import discord
from os import getcwd

try:
    error_messages_q
except NameError:
    error_messages_q = Queue()

def uiLogging():
    '''() -> Logger class
    sets up a log so that it outputs to ./addons/UIdea/data/UIdea.log and then returns the log'''
    logger = logging.getLogger('UIdea')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='./addons/UIdea/data/UIdea.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

log = uiLogging()

def report_error(error, description, user=None):
    # print(error.__traceback__)
    # generate error msg
    error_msg = make_msg_from_error(error, description)
    if user:
        # queue up message (for owner) in error queue
        # print(user+':'+error_msg)
        send_error(error_msg, user)
    else:
        # print(error_msg) # debug
        pass
    # log error
    log.warning(description)
    log.error(error)


def report_ui_error(error, ui_json, description):
    if 'discord-log' in ui_json[DEBUG]:
        user = ui_json[INFO][OWNER]
    else:
        user = None
    report_error(error, description, user=user)

def make_msg_from_error(err, desc=''):
    tb = ''.join(traceback.format_exc())
    tb = tb.replace(str(getcwd()), '')
    if desc:
        return desc+'\n'+'Reason:** `%s`** '%str(err)+'```'+tb+'```'
    else:
        return 'Reason:** `%s`** '%str(err)+'```'+tb+'```'

def report_issue(desc, user=None):
    if user:
        # queue up msg to send to user
        # print(user+':'+desc)
        send_issue(desc, user)
    else:
        # print(desc) # debug
        pass
    # log error
    log.info(desc)

def send_issue(content, user):
    action_dict = { plugin.ThreadedPlugin.SEND_MESSAGE:{plugin.ARGS:list(), plugin.KWARGS:dict()} }
    action_dict[plugin.ThreadedPlugin.SEND_MESSAGE][plugin.ARGS].append(user)
    em = embed.create_embed(title='A UIssue occured during execution', description=content, footer={'text':'You are receiving this because you are the owner', 'icon_url':None}, colour=0xffff11)
    action_dict[plugin.ThreadedPlugin.SEND_MESSAGE][plugin.KWARGS]['embed']=em
    error_messages_q.append(action_dict)

def send_error(content, user):
    action_dict = { plugin.ThreadedPlugin.SEND_MESSAGE:{plugin.ARGS:list(), plugin.KWARGS:dict()} }
    action_dict[plugin.ThreadedPlugin.SEND_MESSAGE][plugin.ARGS].append(user)
    em = embed.create_embed(title='A UI Error occured during execution', description=content, footer={'text':'You are receiving this because you are the owner', 'icon_url':None}, colour=0xff1111)
    action_dict[plugin.ThreadedPlugin.SEND_MESSAGE][plugin.KWARGS]['embed']=em
    error_messages_q.put(action_dict)
