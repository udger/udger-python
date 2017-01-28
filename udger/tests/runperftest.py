import time

from udger import Udger

"""
Running in both Python 2 and Python 3 like this:

$ PYTHONPATH=../.. python2 runperftest.py
$ PYTHONPATH=../.. python3 runperftest.py

"""


udger = Udger('')

uas = [line.rstrip('\n') for line in open('ua.txt')]

start_time = time.time()
step_time = start_time
for i in range(10000):
    ua_string  = uas[i % len(uas)]
    udger.parse_ua(ua_string)
    if (i % 1000) == 0:
        print ("step: ", i, " avg: ", 1000.0/(time.time() - step_time) , "/sec")
        step_time = time.time()
print("Total time: ", i / (time.time() - start_time), "/sec")