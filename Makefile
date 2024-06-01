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
	rasa run --debug --enable-api --cors "*" --endpoints ${REMOTE_DIR}/endpoints.yml --credentials ${REMOTE_DIR}/credentials.yml --port 8888

forward:
	ngrok http --domain=condor-discrete-poorly.ngrok-free.app 8888

action:
	rasa run actions --auto-reload --cors "*"

action-remote:
	ENV=prod rasa run actions --auto-reload --cors "*"


clean: 
	rm -rf ./models