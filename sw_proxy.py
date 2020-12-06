import os
import flask
import atexit
import logging
from flask import jsonify
from insert_ips import InsertIps
from apscheduler.schedulers.background import BackgroundScheduler

from src.Redis.redisEntity import RedisEntity
from src.Redis.errorCacheEntity import ErrorsCache

###########################################
# load configurations from env.variables  #
# or from settings.env in case of docker  #
###########################################
app = flask.Flask(__name__)

logging_levels = {'info': logging.INFO, 'error': logging.ERROR}
redis_hostname = os.environ.get('REDIS_HOSTNAME', "redis")
app.debug = os.environ.get("DEBUG", False)
app.logger.setLevel(logging_levels.get(os.environ.get("LOGGING_LEVEL", 'error')))

# lazy loading redis
print(f"Redis run on: {redis_hostname} \n")
# cache is the DAO where the countries lists resides
cache = RedisEntity()
# errorsCache the error local cache, where the items represents ReportedError ips
errorsCache = ErrorsCache(k=6, logger=app.logger)

# schedule a job to refresh the error cache every 1 minute
scheduler = BackgroundScheduler()
scheduler.add_job(func=errorsCache.insert_back, trigger="interval", seconds=60)
scheduler.start()


@app.route('/')
def home():
    return "proxy server\n"


@app.route('/health')
def health():
    return jsonify({"status": "UP"})


@app.route('/GetProxy/<string:country_code>')
def get_proxy(country_code):
    try:
        app.logger.info(f"GetProxy for country code {country_code}")
        ip = cache.get_from_cache(country_code)
        if ip is None:
            ip = "No ips for this list"
        else:
            ip = ip.decode("utf-8")
        return jsonify({"ip": ip})
    except Exception as e:
        app.logger.error(f"Exception in GetProxy {e}")
        flask.abort(400)


@app.route('/ReportError', methods=['POST'])
def report_error():
    if flask.request.method == 'POST':
        # Extract the input
            try:
                request = flask.request.get_json()

                app.logger.info(f""" ReportError request made for {request['ip']} in list {request['country_code']}""")
                res = errorsCache.suspend_for_k_hours(request['country_code'],
                                                      request['ip'])
                if res > 0:
                    app.logger.info(f"""{request['ip']} in list {request['country_code']}
                                    successfully reported and suspended """)
                    status = 'suspended'

                else:
                    app.logger.error(f"""{request['ip']} in list {request['country_code']} didnt suspended """)
                    status = 'not found'

                return jsonify({"ip": request['ip'], "status": status})
            except Exception as e:
                app.logger.error(f"Exception in ReportError {e}")
                flask.abort(400)


#
InsertIps().insert()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run()
