# coding=utf-8

from bs4 import BeautifulSoup
import urllib
import urllib.request
import urllib.parse
import http.cookiejar
from PIL import Image
import ImagePrinter
import re
import time
# import pytesseract
import os.path

data = {
    "__VIEWSTATE": "dDwtNTE2MjI4MTQ7Oz6pxCBIhRvKaf33f7SsCO02rsKuQQ==",
    "txtUserName": "username",
    "Textbox1": "",
    "TextBox2": "password",
    "txtSecretCode": "",
    "RadioButtonList1": "%D1%A7%C9%FA",
    "Button1": "",
    "lbLanguage": "",
    "hidPdrs": "",
    "hidsc": "",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
}
root = "http://jwgl1.hznu.edu.cn/(thau1c55befhs345k0zbi245)"

# read username and password
if os.path.isfile(os.path.join(os.path.dirname(__file__),"user_info.txt")):
    with open("user_info.txt", "r") as f:
        data["txtUserName"] = f.readline().strip()
        data["TextBox2"] = f.readline().strip()

cookie = http.cookiejar.MozillaCookieJar()
handler = urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(handler)

# --------------------------------------
# try to get the secret code image
# --------------------------------------
request = opener.open(root + "/CheckCode.aspx")
with open("icode.gif","wb") as f:
    f.write(request.read())

# open the secret code image

# ------ auto recognize secret code(failed) --------
# pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
# with Image.open("icode.gif") as img: # show the secret code
#     img = img.convert("L")
#     print(pytesseract.image_to_string(img))
# ---------------------------------------------------

# input by person himself
with Image.open("icode.gif") as img: # show the secret code
    img.show()
    data["txtSecretCode"] = input()


# --------------------------------------
# sent data to login
# --------------------------------------
request = urllib.request.Request(root + "/default2.aspx",
                                 urllib.parse.urlencode(data).encode(), headers)
response = opener.open(request)

# analyse html to get real_name
soup = BeautifulSoup(response, "html.parser")
xhxm = soup.find(id="xhxm")
real_name = ""
if xhxm:
    real_name = xhxm.text[0:-2]
else:
    print("login failed!")
    exit(0)


# --------------------------------------
# jump to major course list page
# --------------------------------------
arg = {
    "xh": data["txtUserName"],
    "xm": real_name,
    "gnmkdm": "N121102",
}
post = {
    "__EVENTTARGET": "kcmcgrid:_ctl11:_ctl0",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "",
    "xx": "",
}
headers["Referer"] = root + "/xs_main.aspx?xh=" + data["txtUserName"]
url = root + "/xsxk.aspx?" + urllib.parse.urlencode(arg, encoding="gb2312")
request = urllib.request.Request(url, headers=headers)
response = opener.open(request)

# get original view state
soup = BeautifulSoup(response, "html.parser")
post["__VIEWSTATE"] = soup.find("input", {"name": "__VIEWSTATE"})["value"]

# get the page list
courseTable = soup.find(id="kcmcgrid")
page_list = ["kcmcgrid:_ctl11:_ctl0"]
try:
    for a in courseTable.find_all("tr")[-1].td.b("a"):
        page_list.append(re.search("kcmcgrid(.*)",a["href"]).group(0).replace("$",":"))
except AttributeError:
    print("Get page list failed!")
    print(courseTable)
    exit(0)

# for each page
for page in page_list:
    post["__EVENTTARGET"] = page
    url = root + "/xsxk.aspx?" + urllib.parse.urlencode(arg,encoding="gb2312")
    request = urllib.request.Request(url, data=urllib.parse.urlencode(post).encode("gb2312"), headers=headers)
    response = opener.open(request)
    # get the course table
    soup = BeautifulSoup(response, "html.parser")
    courseTable = soup.find(id="kcmcgrid")
    for tr in courseTable.contents[2:-2]:
        # 课程代码(1) 课程名称 课程性质 组或模块 学分 周学时 考试时间 课程介绍 选否 余量
        for td in tr.contents[1:11]:
            print(td.text, end=", ")
        print()
    # sleep to avoid defence
    # time.sleep(1)
