import AppOpener as ao

def takes_app(task,app_name):
    if "open" in task or "start" in task:
        ao.open(app_name)
    elif "close" in task or "stop" in task:
        ao.close(app_name)