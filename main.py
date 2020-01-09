# -- coding: utf-8 --
import os
import time
import json
import task

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

DEFAULT_CONFIG_FILE = 'config.json'


def load_config():
    with open(DEFAULT_CONFIG_FILE) as f:
        config_data = f.read()
        _config = json.loads(config_data)
    return _config


if __name__ == '__main__':
    config = load_config()
    tools_path = os.path.join(os.path.abspath(os.path.curdir), 'tools')
    os.environ['PATH'] = '{0};'.format(tools_path) + os.environ['PATH']
    scheduler = BackgroundScheduler()
    trigger = IntervalTrigger(seconds=config.get('cycle', 3))
    scheduler.add_job(task.backup, trigger, kwargs=config)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
    exit(0)
