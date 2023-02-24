.PHONY: airflow_variables.json

dev: airflow_connect/tests/rsconnect_keys.json

dev-start:
	docker-compose up -d

airflow_connect/tests/rsconnect_keys.json: dev-start
	docker-compose exec -T rsconnect bash < script/setup-rsconnect/add-users.sh
	sleep 7
	curl -s --retry 10 --retry-connrefused http://localhost:9082
	python script/setup-rsconnect/dump_api_keys.py http://localhost:9082 $@

airflow_variables.json: rsconnect_keys.json
	cat $^ \
		| jq '{"connect_api_key": .admin, "connect_server": "http://rsconnect:3939"}' \
		> $@
