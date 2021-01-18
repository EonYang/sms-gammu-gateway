import os

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import load_user_data, init_state_machine

pin = os.getenv('PIN', None)
ssl = os.getenv('SSL', False)
user_data = load_user_data()
machine = init_state_machine(pin)
app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    return username == user_data['username'] and \
        password == user_data['password']


class Sms(Resource):

    def __init__(self, sm):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('text')
        self.parser.add_argument('number')
        self.parser.add_argument('smsc')
        self.machine = sm

    # @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        if args['text'] is None or args['number'] is None:
            abort(404, message="Parameters 'text' and 'number' are required.")
        result = [machine.SendSMS({
            'Text': args.get("text"),
            'SMSC': {'Number': args.get("smsc")} if args.get("smsc") else {'Location': 1},
            'Number': number,
        }) for number in args.get("number").split(',')]
        return {"status": 200, "message": str(result)}, 200


class Signal(Resource):
    def __init__(self, sm):
        self.machine = sm

    def get(self):
        return machine.GetSignalQuality()


class Getsms(Resource):
    def __init__(self, sm):
        self.machine = sm

    # @auth.login_required
    def get(self):

        smss = []
        status = self.machine.GetSMSStatus()
        remain = status['SIMUsed'] + \
            status['PhoneUsed'] + status['TemplatesUsed']

        start = True

        try:
            while remain > 0:
                if start:
                    sms = self.machine.GetNextSMS(Start=True, Folder=0)
                    start = False
                else:
                    sms = self.machine.GetNextSMS(
                        Location=sms[0]['Location'], Folder=0
                    )
                remain = remain - len(sms)

                for m in sms:
                    print()
                    smss.append(m)
                    # print('{0:<15}: {1}'.format('Number', m['Number']))
                    # print('{0:<15}: {1}'.format('Date', str(m['DateTime'])))
                    # print('{0:<15}: {1}'.format('State', m['State']))
                    # print('\n{0}'.format(m['Text']))
        except gammu.ERR_EMPTY:
            pass
            # This error is raised when we've reached last entry
            # It can happen when reported status does not match real counts
        return smss


if user_data['username'] is not None:
    Sms.post = auth.login_required(Sms.post)
    Getsms.get = auth.login_required(Getsms.get)

api.add_resource(Sms, '/sms', resource_class_args=[machine])
api.add_resource(Signal, '/signal', resource_class_args=[machine])
api.add_resource(Getsms, '/getsms', resource_class_args=[machine])

if __name__ == '__main__':

    if ssl:
        app.run(port='5000', host="0.0.0.0", ssl_context=(
            '/ssl/cert.pem', '/ssl/key.pem'))
    else:
        app.run(port='5000', host="0.0.0.0")
