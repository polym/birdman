# gunicorn config
bind = ("0.0.0.0:8888")
daemon = False

accesslog = '/tmp/bm_access.log'

proc_name = 'Birdman:0.1.0'

# birdman config
username = ''
password = ''
