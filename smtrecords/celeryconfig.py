broker_url = 'amqp://strings:swordfish@localhost:5672/strings'
result_backend = 'rpc'

task_serializer = 'json'
accept_content=['json']
timezone = 'UTC'
enable_utc = True

task_routes = {
    'smtrecords.worker_tasks.build_z3': {'queue': 'build'},
    'smtrecords.worker_tasks.benchmark_instance': {'queue': 'benchmark'},
    'smtrecords.worker_tasks.validate_instance': {'queue': 'validate'}
}

# limit prefetch for long-running tasks
worker_prefetch_multiplier = 1
