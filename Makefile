install:
	pip install -r requirements.txt

test:
	pytest orchestrator/tests edge/tests cloud/tests

run-edge:
	python edge/app.py

run-cloud:
	python cloud/app.py

run-orchestrator:
	python orchestrator/orchestrator.py
