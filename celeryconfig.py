broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
worker_hijack_root_logger = False
task_track_started = True
