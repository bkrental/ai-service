LOCAL_DIR = ./environments/local
REMOTE_DIR = ./environments/remote

train:
	rasa train

shell-local: 
	rasa shell --debug --enable-api --endpoints ${LOCAL_DIR}/endpoints.yml --credentials ${LOCAL_DIR}/credentials.yml

shell-remote: 
	rasa shell --debug --enable-api --endpoints ${REMOTE_DIR}/endpoints.yml --credentials ${REMOTE_DIR}/credentials.yml

run-local:
	rasa run --enable-api --cors "*" --endpoints ${LOCAL_DIR}/endpoints.yml --credentials ${LOCAL_DIR}/credentials.yml --port 5005

run-remote:
	rasa run --enable-api --cors "*" --endpoints ${REMOTE_DIR}/endpoints.yml --credentials ${REMOTE_DIR}/credentials.yml --port 5005 & ngrok http 5005

action:
	rasa run actions --auto-reload --cors "*"

clean: 
	rm -rf ./models