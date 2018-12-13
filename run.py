import os
import atexit
from apscheduler.scheduler import Scheduler

from flask import Flask

import settings

app = Flask(__name__)

def voting_list():
    # main func

def control_flow():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(seconds=60*10)
    def job_function():
        if voting_power(settings.Username) >= settings.Limit_voting_power:
            print('Vote')
            pass

    atexit.register(lambda: cron.shutdown(wait=False))


def clear_list():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(days=4)
    def job_function():
        # link file removed.

    atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    try:
        control_flow()
        clear_list()
    except:
        pass

    port = int(os.environ.get('PORT', 9090))
    app.run(host='0.0.0.0', port=port)
