build:
	docker buildx build --platform linux/amd64,linux/arm64 -t yy2473/mail_me_my_sms:arm-latest --push .

install:
	pip install -e .

dev: install
	pip install -e '.[dev]'

start:
	source ./sendgrid.env && python3 ./mail_me_my_sms/main.py

server:
	source ./sendgrid.env && python3 ./mail_me_my_sms/server.py

test:
	source ./sendgrid.env && pytest tests -k re