import os

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import reqparse, Api, Resource, abort

from support import (
    load_user_data,
    init_state_machine,
    getAndDeleteAllSMS)

pin = os.getenv('PIN', None)
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
            'SMSC': {'Number': args.get("smsc")
                     } if args.get("smsc") else {'Location': 1},
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
        entries = getAndDeleteAllSMS(self.machine)

        for sms in entries:
            sms_dict = {}
            sms_dict["Date"] = str(sms[0]['DateTime'])
            sms_dict["Number"] = str(sms[0]['Number'])
            sms_dict["State"] = str(sms[0]['State'])
            sms_dict["Text"] = ''.join(
                [msg['Text'] for msg in sms]
            )
            smss.append(sms_dict)

        return smss


if user_data['username'] is not None:
    Sms.post = auth.login_required(Sms.post)
    Getsms.get = auth.login_required(Getsms.get)

api.add_resource(Sms, '/sms', resource_class_args=[machine])
api.add_resource(Signal, '/signal', resource_class_args=[machine])
api.add_resource(Getsms, '/getsms', resource_class_args=[machine])

if __name__ == '__main__':
    app.run(port='5000', host="0.0.0.0")
