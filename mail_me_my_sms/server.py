from fastapi import FastAPI
from mail_me_my_sms.redis_helper import RedisDict
import uvicorn
from datetime import datetime

app = FastAPI()

inbox = RedisDict('sms:inbox')
sent = RedisDict('sms:sent')
spam = RedisDict('sms:spam')


def get_sorted(d: RedisDict):
    entries = [(s['date'], s) for s in d.all().values()]
    return sorted(
        entries,
        key=lambda x: datetime.now() - datetime.strptime(
            x[0], "%Y-%m-%d %H:%M:%S"))


def _get_inbox():
    return list(inbox.all().values())


def _get_sent():
    return get_sorted(sent)


def _get_spam():
    return list(spam.all().values())


@app.get("/")
async def get_all():
    return {
        "inbox": _get_inbox(),
        "sent": _get_sent(),
        "spam": _get_spam(),
    }


@app.get("/inbox")
async def get_inbox():
    return _get_inbox()


@app.get("/sent")
async def get_sent():
    return _get_sent()


@app.get("/spam")
async def get_spam():
    return _get_spam()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=4000)
