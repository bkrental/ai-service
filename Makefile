LOCAL_DIR = ./environments/local
REMOTE_DIR = ./environments/remote

train:
	rasa train

shell-local: 
	rasa shell --debug --enable-api --endpoints ${LOCAL_DIR}/endpoints.yml --credentials ${LOCAL_DIR}/credentials.yml

shell-remote: 
	rasa shell --debug --enable-api --endpoints ${REMOTE_DIR}/endpoints.yml --credentials ${REMOTE_DIR}/credentials.yml


action:
	rasa run actions --auto-reload --cors "*"

freeze-local:
	pip3 freeze >> ${LOCAL_DIR}/requirements.txt

freeze-remote:
	pip3 freeze >> ${REMOTE_DIR}/requirements.txt

clean: 
	rm -rf ./models