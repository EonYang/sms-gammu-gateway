import sys
import os
import gammu


def load_user_data():
    users = {
        'username': os.environ.get('USER_ID'),
        'password': os.environ.get('USER_PASSWORD')
    }
    return users


def init_state_machine(pin, filename='gammu.config'):
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
