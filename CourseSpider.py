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
import json


res = {
    "course_list": [],
    "institute_list": [],
}
data = {
    "__VIEWSTATE": "dDwtNTE2MjI4MTQ7Oz6pxCBIhRvKaf33f7SsCO02rsKuQQ==",
    "txtUserName": "username",
    "TextBox2": "password",
    "txtSecretCode": "",
    "RadioButtonList1": "%D1%A7%C9%FA",
    "Button1": "",
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
# calculate course list page url
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
}
main_page_url = root + "/xs_main.aspx?xh=" + data["txtUserName"]
course_list_url = root + "/xsxk.aspx?" + urllib.parse.urlencode(arg, encoding="gb2312")

# --------------------------------------
# jump to major list window
# --------------------------------------
major_list_url = root + "/zylb.aspx?xh={0}&nj={1}".format(data["txtUserName"], data["txtUserName"][0:4])
headers["Referer"] = course_list_url
request = urllib.request.Request(major_list_url, headers=headers)
response = opener.open(request)
soup = BeautifulSoup(response, "html.parser")
post["__VIEWSTATE"] = soup.find("input", {"name": "__VIEWSTATE"})["value"]
institute_select = soup.find("select", id="DropDownList2")
year_list = [x.text for x in soup.find("select", id="DropDownList1").find_all("option")]
print(year_list)
major_cnt = 0
print(institute_select.find_all("option"))
for option in institute_select.find_all("option"):
    institute = {
        "institute_name": option.text,
        "grades": []
    }
    for year in year_list:
        post["__EVENTTARGET"] = "DropDownList2"
        post["xx"] = "zx"
        post["DropDownList2"] = option["value"]
        post["DropDownList1"] = year
        post["RadioButtonList1"] = "2"
        headers["Referer"] = major_list_url
        request = urllib.request.Request(major_list_url, urllib.parse.urlencode(post).encode("gb2312"), headers)
        # time.sleep(3)
        response = opener.open(request)
        grade = {
            "grade_name": year,
            "majors": []
        }
        soup = BeautifulSoup(response, "html.parser")
        for major_option in soup.find("select", id="ListBox1").find_all("option"):
            grade["majors"].append({
                "major_name": major_option.text
            })
            major_cnt = major_cnt + 1
            print("major_cnt:",major_cnt)
        if len(grade["majors"]) > 0:
            institute["grades"].append(grade)
    res["institute_list"].append(institute)

with open("res.json", "wb") as f:
    json_res = json.dumps(res, indent=4, ensure_ascii=False)
    f.write(json_res.encode())
print(json_res)

# # --------------------------------------
# # jump back major course list page
# # --------------------------------------
# headers["Referer"] = main_page_url
# request = urllib.request.Request(course_list_url, headers=headers)
# response = opener.open(request)
#
# # get original view state
# soup = BeautifulSoup(response, "html.parser")
# post["__VIEWSTATE"] = soup.find("input", {"name": "__VIEWSTATE"})["value"]
#
# # get the page list
# courseTable = soup.find(id="kcmcgrid")
# page_list = ["kcmcgrid:_ctl11:_ctl0"]
# try:
#     for a in courseTable.find_all("tr")[-1].td.b("a"):
#         page_list.append(re.search("kcmcgrid(.*)",a["href"]).group(0).replace("$",":"))
# except AttributeError:
#     print("Get page list failed!")
#     print(courseTable)
#     exit(0)
#
# # for each page
# for page in page_list:
#     post["__EVENTTARGET"] = page
#     course_list_url = root + "/xsxk.aspx?" + urllib.parse.urlencode(arg, encoding="gb2312")
#     request = urllib.request.Request(course_list_url, data=urllib.parse.urlencode(post).encode("gb2312"), headers=headers)
#     response = opener.open(request)
#     # get the course table
#     soup = BeautifulSoup(response, "html.parser")
#     courseTable = soup.find(id="kcmcgrid")
#     for tr in courseTable.contents[2:-2]:
#         # 课程代码(1) 课程名称 课程性质 组或模块 学分 周学时 考试时间 课程介绍 选否 余量
#         for td in tr.contents[1:11]:
#             print(td.text, end=", ")
#         print()
#     # sleep to avoid defence
#     # time.sleep(1)
