# Curation Bot

This bot was created to catch curation from the steemit posts.

## Install

Enter the file directory.
```
pip install -r requirements.txt
touch settings_local.py
```

Example settings_local.py
```
username = 'username'
steem_key = 'token'
```

and start!

```
python run.py
```

## How does it work?

Now it's only follows the utopian post. Its checks and votes in periods. This is very simple now.


## Roadmap

- Logs to be added.
- DB integration. (SQL)
- Multiple members' created posts will be followed.
- It will be controlled by the web. Results will be displayed.
- Telegram bot will be integrated.