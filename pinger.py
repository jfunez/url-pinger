import os
import datetime
import socket
import requests
from flask import Flask, render_template


SITES_TXT = os.getenv("SITES_TXT", "sites.txt")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "1"))
REFRESH_TIMEOUT = float(os.getenv("REFRESH_TIMEOUT", "60"))

app = Flask(__name__)


@app.route('/')
def home():
    sites = open(SITES_TXT).readlines()
    result = []
    for line in sites:
        site, auth = extract_site_and_auth(line.strip())
        try:
            response = requests.get(site, timeout=REQUEST_TIMEOUT, allow_redirects=True, auth=auth)
            assert response.text != ''
            assert response.status_code == 200
        except (requests.exceptions.RequestException, socket.timeout, AssertionError) as err:
            print("Failed to read {0} (timeout={1})".format(site, REQUEST_TIMEOUT))
            result.append((site, "fail"))
        else:
            result.append((site, "ok"))
    now = datetime.datetime.now()
    template_vars = dict(
        result=result,
        last_update=now,
        refresh_timeout=REFRESH_TIMEOUT)
    return render_template('pinger.html', **template_vars)


def extract_site_and_auth(line):
    if ' ' in line:
        site, auth = line.rsplit(' ', 1)
        user, password = auth.split(':')
        return (site, (user, password))
    else:
        return [line, ()]


if __name__ == '__main__':
    app.run(debug=True)


