import json


from src import worker
from src.database import database


#
@worker.task_manage.task(name="hello_task")
@worker.sync_task
async def hello_task(data):
    print("database.is_connected", database.is_connected)
    return {
        "status": 1,
        "result": "oke"
    }
