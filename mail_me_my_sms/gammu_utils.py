import sys
import os
import gammu._gammu as gammu


def load_user_data():
    users = {
        'username': os.environ.get('USER_ID'),
        'password': os.environ.get('USER_PASSWORD')
    }
    return users


def init_state_machine(pin=None, filename='gammu.config'):
    sm = gammu.StateMachine()
    sm.ReadConfig(Filename=filename)
    sm.Init()

    if sm.GetSecurityStatus() == 'PIN':
        if pin is None or pin == '':
            print("PIN is required.")
            sys.exit(1)
        else:
            sm.EnterSecurityCode('PIN', pin)
    return sm


def getAndDeleteAllSMS(state_machine):
    # Read SMS memory status ...
    memory = state_machine.GetSMSStatus()
    # ... and calculate number of messages
    remaining = memory["SIMUsed"] + memory["PhoneUsed"]

    # Get all sms
    start = True
    entries = list()

    try:
        while remaining > 0:
            if start:
                entry = state_machine.GetNextSMS(Folder=0, Start=True)
                start = False
            else:
                entry = state_machine.GetNextSMS(
                    Folder=0, Location=entry[0]["Location"]
                )

            remaining = remaining - 1
            entries.append(entry)

            # delete retrieved sms
            state_machine.DeleteSMS(Folder=0, Location=entry[0]["Location"])

    except gammu.ERR_EMPTY:
        # error is raised if memory is empty (this induces wrong reported
        # memory status)
        print('Failed to read messages!')

    # Link all SMS when there are concatenated messages
    entries = gammu.LinkSMS(entries)

    return entries
