import csv
import sys
# egain_apr2014.csv
def process(date, symbol):
    print(date, symbol)

from io import StringIO
with open('tab_delimited_stock_prices.txt', 'rb') as f:
  oldreader = StringIO(f.read().decode())
  reader = csv.reader(oldreader, delimiter = '\t')
  for row in reader:
   data = row[0]
   symbol = row[1]
   closing_price = float(row[2])
   process(data, symbol)


#
#import data
#
from io import StringIO
with open('egain_apr2014.csv', 'rb') as f:
  oldreader = StringIO(f.read().decode())
  reader = csv.reader(oldreader, delimiter = '\t')
  for row in reader:
    print(row)

import csv
ifile  = open('egain_apr2014.csv')
read = csv.reader(ifile)
for row in read:
    print (row)

from sys import getfilesystemencoding
def format_filename(filename):
    return str(filename, getfilesystemencoding(),'replace')

print(format_filename('egain_apr2014.csv'))

from bs4 import BeautifulSoup
import requests

# region Description
url = "http://shop.oreilly.com/category/browse-subjects/programming/python.do"
# endregion
#soup = BeautifulSoup(requests.get(url).text, 'html5lib')
#tds = soup('td','thumbtext')


import math
from probability import inverse_normal_cdf
import random
import PaCal
import scipy

def random_normal():
    return inverse_normal_cdf(random.random())

xs = [random_normal() for _ in range(1000)]
ys1 = [ x+ random_normal()/2 for x in xs]
ys2 = [-x+ random_normal()/2 for x in xs]


import os
os.getcwd()
#os.environ

even_numbers = [x for x in range(50) if x%2 ==0]
squares = [x*x for x in range(5)]

square_dick = {x: x*x for x in range(5)}
square_set = {x*x for x in [1,-1]}

pairs = {(x,y)
         for x in range(10)
         for y in range(10)}
from matplotlib import pyplot as plt
years = [1950, 1960, 1970, 1980, 1990, 2000, 2010 ]
gdp = [-300.2, 543.3, 1075.9, 2862.5, 5979.6, 10289.7, 14985.3]

plt.plot(years, gdp, color = 'green', marker = 'o', linestyle = 'solid')
plt.title("Nominal GDP")
plt.ylabel("Billions of $")
plt.show()



# IPython log file


import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['Y:\\Studying\\Python\\StudyProject'])
a =1
a
# 'a' in _ip.user_ns
# get_ipython().magic('pinfo %reset')
# 'a' in _ip.user_ns
# get_ipython().magic('time')
# def add_numbers(a,b):
#     """
#     Add two numbers together
#     Returns
#     :param a:
#     :param b:
#     :return:
#     """
#     return a+b
# get_ipython().magic('time add_number(1,2)')
# get_ipython().magic('time add_numbers(1,2)')
# get_ipython().magic('timeit add_numbers(1,2)')
# get_ipython().magic('who')
# get_ipython().magic('who_ls')
# get_ipython().magic('whos')
# qtconsole --pylab=inline
# qtconsole
# get_ipython().magic('run ipython')
# get_ipython().magic('logstart')
# get_ipython().magic('logstate')
# get_ipython().magic('logon')
# def add_numbers(a,b):
#     """
#     Add two numbers together
#     Returns
#     :param a:
#     :param b:
#     :return:
#     """
#     return a+b
# get_ipython().magic('dir')
# get_ipython().magic('dirs')
# get_ipython().magic('dhist')
# get_ipython().system('python')
