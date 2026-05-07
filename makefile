run:
	uvicorn app.main:app --reload

prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 6

aws-prod:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8

locust-local:
	locust -f locustfile.py --host=http://127.0.0.1:8000

locust-aws:
	locust -f locustfile.py --host=http://13.233.255.137:8000

locust-master:
	locust -f locustfile.py --master --host=http://13.233.255.137:8000

locust-worker:
	locust -f locustfile.py --worker --master-host=127.0.0.1