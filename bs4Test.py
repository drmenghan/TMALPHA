import os
from bs4 import BeautifulSoup
import requests
import re
soup = BeautifulSoup(open("test.html"))
soup.contents.__sizeof__()

print()

soup.find("python")
soup("Python")

tds = soup('td','thumbtext')
#for td in tds:

def book_info(td):
    title = td.find("div","thumbheader").a.text
    author_name = td.find('div', 'AuthorName').text
    authors = [x.strip() for x in re.sub("^By ","", author_name).split(",")]
    isbn_link = td.find("div", "thumbheader").a.get("href")
    isbn = re.match("/product/(.*)\.do", isbn_link).groups()[0]
    date = td.find("span", "directorydate").text.strip()

    return{
        "title":title,
        "authors":authors,
        "isbn":isbn,
        "date":date
    }
for td in tds:
    print(book_info(td))


from lxml import html
import requests

page = requests.get("test.html")
tree = html.fromstring(str(open("test.html")))

print(tree)

mainDirectory = "/"
ProjectData = "Y:\Projects\TMalpha\May15_transcripts"
import glob
print(glob.glob(mainDirectory))

import os
from os import listdir
x = os.listdir(ProjectData)
len(x)
x[1]



from numpy import pi, sin, cos, mgrid
dphi, dtheta = pi/250.0, pi/250.0
[phi,theta] = mgrid[0:pi+dphi*1.5:dphi,0:2*pi+dtheta*1.5:dtheta]
m0 = 4; m1 = 3; m2 = 2; m3 = 3; m4 = 6; m5 = 2; m6 = 6; m7 = 4;
r = sin(m0*phi)**m1 + cos(m2*phi)**m3 + sin(m4*theta)**m5 + cos(m6*theta)**m7
x = r*sin(phi)*cos(theta)
y = r*cos(phi)
z = r*sin(phi)*sin(theta)

# View it.
from mayavi import mlab
s = mlab.mesh(x, y, z)
mlab.show()
