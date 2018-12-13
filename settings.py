# Curation Config
type = 'function'
results = 'utopian.py'

## Alternative Config
# type = 'list'
# results = ['123', '32']

# User Config
limit_power = 80
username = 'bot'
steem_key = 'key'

try:
    from settings_local import *
except:
    pass