web: gunicorn manage:app
worker: python -u manage.py run_worker
init: python manage.py recreate_db && python manage.py setup_dev && python manage.py add_fake_data
