build-arm:
	docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t yy2473/gammu-sms-gateway:arm-latest --push .