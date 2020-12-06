
############################################
###      introduction to the service      ##
############################################

I decided to implement the ip's storage(cache) in redis.
The key reason is *availability*, we can deploy the service across geographically locations(for late latencies) or/and use load balancing techniques to route requests
to few instances, hence we can ensure that the cyclic order kept, it is not happening in the service resolution, but in redis

I use redis list for each country code: and for each request I do "left pop" and "right push" to ensure round robin uses of the ips.
Handle ErrorReport:
     the reported ip will be removed from it's list by redis-remove function, and will be saved in local storage for 6 hours(epoch time). 
     I built a function that has scheduler will run in interval time(1 minute), 
     and will insert back the ips that were suspended for 6 hours
     


**** the tests file is only for local/docker checks

############################################
###       run it with docker-compose      ##
############################################

1. edit the settings.env file in case you want to see full logs
2. *docker-compose up --build*
3. go to http://0.0.0.0:5000/health to check if service is up
4. http://0.0.0.0:5000/GetProxy/<country_code> to get ip for <country_code> e.g http://0.0.0.0:5000/GetProxy/us
5. POST request to http://0.0.0.0:5000/ReportError with json e.g {"ip":"209.146.129.32",
                                                                  "country_code":"us"}
   don't forget to add header Content-Type:application/json


############################################
###       run it with pycharm             ##
############################################

1. brew install redis
2. locally start redis server: redis-server
3. redis-cli shutdown
4. install venv:
    pip install virtualenv
    virtualenv -p python3.7 venv
    source venv/bin/activate
    pip install -r requirements.txt
5. add env variable REDIS_HOSTNAME=localhost
6. run the sw_proxy.py
7. go to http://127.0.0.1:5000/health to check if service is up
8. http://127.0.0.1:5000/GetProxy/<country_code> to get ip for <country_code> e.g http://127.0.0.1:5000/GetProxy/us
9. POST request to http://127.0.0.1:5000/ReportError with json e.g {"ip":"209.146.129.32", "country_code":"us"} don't forget to add header



