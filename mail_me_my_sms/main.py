
from mail_me_my_sms.config import CONF
import re
from mail_me_my_sms.email_utils import send_to_me
from mail_me_my_sms.model import SMS
import hashlib
import traceback
from typing import List
from mail_me_my_sms.gammu_utils import (
    init_state_machine,
    getAndDeleteAllSMS)
from time import sleep
from mail_me_my_sms.redis_helper import RedisDict

import logging
logging.basicConfig()
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
inbox = RedisDict('sms:inbox')
sent = RedisDict('sms:sent')
spam = RedisDict('sms:spam')
lg.info('init gammu')
machine = init_state_machine()


def is_spam(sms: SMS):
    found = re.findall("(退订|退.+T|赢.+奖|验证码)", sms.text)
    return len(found) > 0 and '验证码' not in found


def key(sms: SMS):
    hash_obj = hashlib.md5(sms.text.encode('utf8'))
    return hash_obj.hexdigest()


def get_all_smss() -> List[SMS]:
    smss: List[SMS] = []
    entries = getAndDeleteAllSMS(machine)

    for sms in entries:
        s = SMS()
        s.date = str(sms[0]['DateTime'])
        s.number = str(sms[0]['Number'])
        s.state = str(sms[0]['State'])
        s.text = ''.join(
            [msg['Text'] for msg in sms]
        )
        if is_spam(s):
            s.spam = True
        smss.append(s)

    return smss


def save_to_inbox(smss: List[SMS]):
    for sms in smss:
        k = key(sms)
        inbox.set(k, sms.dict())


def sms_to_html(sms: SMS):
    return f'''
    <div>
    <h3> From {sms.number} </h3>
    <p>{sms.text}</p>
    </div>
    '''


def move_from_A_to_B(k: str, A: RedisDict, B: RedisDict):
    sms = A.get(k)
    B.set(k, sms)
    A.remove(k)


def move_from_inbox_to_sent(k: str):
    sms = inbox.get(k)
    sent.set(k, sms)
    inbox.remove(k)


def move_from_inbox_to_spam(k: str):
    sms = inbox.get(k)
    spam.set(k, sms)
    inbox.remove(k)


def get_to_send():
    sent_keys = set()
    to_send: List[str] = []

    for k, val in inbox.all().items():
        sms = SMS(**val)
        if sms.spam:
            move_from_inbox_to_spam(k)
        else:
            to_send.append(sms_to_html(sms))
            sent_keys.add(k)

    return to_send, sent_keys


def work():
    lg.info('start working')
    count = 0
    while True:
        lg.info(f'signal: {machine.GetSignalQuality()}')
        try:
            smss = get_all_smss()
            count += 1
            if len(smss) != 0:
                lg.info(len(smss))
                save_to_inbox(smss)

            to_send, sent_keys = get_to_send()
            if len(to_send) > 0:
                send_to_me('<br/>'.join(to_send))
                for k in sent_keys:
                    move_from_inbox_to_sent(k)

        except Exception as e:
            traceback_list = traceback.format_tb(e.__traceback__)
            lg.error(f"""
                'error': {str(e)},
                'class': {e.__class__.__name__},
                'traceback': {traceback_list}
                """)

        sleep(CONF.SMS_CHECK_INTERVAL)


if __name__ == '__main__':
    work()
