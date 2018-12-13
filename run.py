import os

import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask

from utils import Curation, get_vp, get_rc, post_vote
import settings

app = Flask(__name__)

voted_txt = 'voted.txt'

def vote_list():
    if not get_vp(settings.username) >= settings.limit_power and get_rc < 0.1 :
        return []
    return Curation('function', settings.results).result


def voted_list():
    with open(voted_txt, 'w') as file:
        lines = file.read().splitlines()
    return lines

def voting_list(votings):
    for voting in votings:
        username = list(filter(lambda x: '@' in x, voting))
        try:
            post_vote(settings.username, username, voting, 100)
            with open(voted_txt, "a") as f:
                f.write("{}\n".format(voting))
        except:
            pass
    print('TODO: Logger.info(Done!)')

def control_flow():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(seconds=60*10)
    def job_function():
        _vote_list = vote_list()
        _voted_list = voted_list()
        voting = list(set(_vote_list) - set(_voted_list))
        voting_list(voting)


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
