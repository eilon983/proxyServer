import unittest
import requests
import os
import json
from collections import Counter


class ProxyServerTests(unittest.TestCase):

    # if you run it via pycharm set env variable SERVER: 127.0.0.1
    server = os.environ.get('SERVER', "0.0.0.0")

    def setUp(self):
        pass

    def test_many_ips(self):
        ips = []
        for x in range(10000):
           ip = requests.get(f'http://{self.server}:5000/GetProxy/us')
           ips.append(json.loads(ip.content)['ip'])
        ctr = Counter(ips)
        num_most_common = ctr.most_common(1)[0][1]
        num_least_common = ctr.most_common(len(ctr))[0][1]
        self.assertEqual(num_most_common, num_least_common)


    def test_report_error(self):
        ips = []
        for x in range(10000):
            ip = requests.get(f'http://{self.server}:5000/GetProxy/us')
            ip = json.loads(ip.content)['ip']
            ips.append(ip)
            res = requests.post(f'http://{self.server}:5000/ReportError', json={"ip": ip, "country_code": "us"})
            res = json.loads(res.content)['status']
            self.assertEqual(res, "suspended")

        for ip in ips:
            res = requests.post(f'http://{self.server}:5000/ReportError', json={"ip": ip, "country_code": "us"})
            res = json.loads(res.content)['status']
            self.assertEqual(res, "not found")
