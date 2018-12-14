import os
import logging

import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask

from utils import Curation, Steemit
import settings

app = Flask(__name__)

voted_txt = 'voted.txt'
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


class PostVote:

    def __init__(self):
        self.vote = self.vote_list()
        self.voted = self.voted_list()
        self.steemit = Steemit(settings.username)

    def vote_list(self):
        if not self.steemit.get_vp(settings.username) >= settings.limit_power and self.steemit.get_rc() < 0.1 :
            return []
        return Curation(settings.type, settings.results).result

    def voted_list(self):
        with open(voted_txt, 'w') as file:
            lines = file.read().splitlines()
        return lines

    def voting_list(self):
        votings = list(set(self.vote) - set(self.voted))
        for voting in votings:
            username = list(filter(lambda x: '@' in x, voting))
            try:
                self.steemit.post_vote(username, voting, 100)
                with open(voted_txt, "a") as f:
                    f.write("{}\n".format(voting))
            except:
                pass
        logging.info('TODO: Logger.info(Done!)')

    def removed_list(self):
        with open(voted_txt, "w") as f:
            f.write('')

def control_flow():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(seconds=60*10)
    def job_function():
        vote_commit = PostVote()
        vote_commit.voting_list()

    atexit.register(lambda: cron.shutdown(wait=False))


def clear_list():
    cron = Scheduler(daemon=True)
    cron.start()

    @cron.interval_schedule(days=4)
    def job_function():
        vote_commit = PostVote()
        vote_commit.removed_list()

    atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    try:
        control_flow()
        clear_list()
    except:
        pass

    port = int(os.environ.get('PORT', 9090))
    app.run(host='0.0.0.0', port=port)
