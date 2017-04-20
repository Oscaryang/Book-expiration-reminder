__author__ = 'Oscar_Yang'
#-*- coding= utf-8 -*-
import subprocess
import sys
import os
import requests
import re
import random
import time
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pytesseract
from PIL import Image

def login(name, password):
    random_num = random.random()  # 生成随机数，构造获取验证码的链接
    url = 'http://202.206.242.99//reader/captcha.php?' + str(random_num)

    get_captcha = session.get(url).content #the output type of r.content is bytes

    with open('captcha.png', 'wb') as f:
        f.write(get_captcha)
        f.close()

    # '''
    #     这段代码是为了方便我们打开图片，它可以直接打开图片
    #     我们就不用去文件夹里去找,里面是判断使用什么系统，
    #     不同系统打开方式有点差异，可以找python文档了解这部分内容
    # '''
    # if sys.platform.find('darwin') >= 0:
    #     subprocess.call(['open', 'captcha.png'])
    # elif sys.platform.find('linux') >= 0:
    #     subprocess.call(['xdg-open', 'captcha.png'])
    # else:
    #     os.startfile('captcha.png')

    image = Image.open('captcha.png')
    code = pytesseract.image_to_string(image)

    # input_captcha = input('请输入验证码：')
    # input_captcha=random_num
    input_captcha = str(code)

    # 构造登录表单，里面就是我们上面提及的四项
    post_data = {
        'number': name,
        'passwd': password,
        'captcha': input_captcha,
        'select': 'cert_no'
    }

    login_url = 'http://202.206.242.99/reader/redr_verify.php'

    html = session.post(login_url, data=post_data).content

    book_hist_url = 'http://202.206.242.99/reader/book_lst.php'
    # content = session.get(book_hist_url).content.decode('utf-8')
    content=session.get(book_hist_url)
    content.encoding="utf8"
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(content.text,"lxml")
    return soup

def get_rec_data(id):
    res=requests.get("http://202.206.242.99/data/data_visual_book.php?id={}".format(id))
    res.encoding="utf8"
    soup=BeautifulSoup(res.text,"lxml")
    names=re.findall(r'name="(.*?)"',str(soup))
    ids=re.findall(r'id="(.*?)"',str(soup))
    item_urls=["http://202.206.242.99/opac/item.php?marc_no={}".format(id) for id in ids]
    rec_item_lists=[]
    for name,item_url in zip(names,item_urls):
        data={"书名":name,"打开链接":item_url}
        rec_item_lists.append(data)
    return rec_item_lists[1:8]

def get_data(soup):
    titles=soup.select("a.blue")
    deadlines=soup.select("font")[1:]
    item_urls=soup.select("a.blue")

    ids=re.findall(r'no=(.*?)"',str(item_urls))
    recs=map(get_rec_data,ids)
    base_data_list=[]
    for title,deadline,item_url,rec in zip(titles,deadlines,item_urls,recs):
        base_data={
            "title":title.text,
            "deadline":deadline.text.strip(),
            "item_url":"http://202.206.242.99/"+item_url["href"],
            "rec":rec
        }
        # print(data)
        base_data_list.append(base_data)
    return base_data_list


def get_detail_data(item_url):
    res=requests.get(item_url)
    res.encoding="utf8"
    soup=BeautifulSoup(res.text,"lxml")
    intro=soup.find_all(class_="sharing_zy")
    # tupus="http://202.206.242.99/"+soup.select("p > a > img")[0]["src"]
    intro=re.findall(r'href="(.*?)"',str(intro))
    # data={
    #     "tupu：":tupus,
    #     "xiangxi：":intro
    # }
    print(intro)
    # return data


def send_email(to_addr,deadline,title,item_url, day,name,rec):
    from_addr = '286073725@qq.com'
    password = '*24865TFBHg*'
    to_addr = '202739494@qq.com'
    smtp_server = 'smtp.qq.com'

    msg=MIMEText('''hello:\n\n    《{}》这本书还有{}天到期，deadline为{}，尽快去还吧！\n      点击链接查看图书详情{}\n     ----------------------------------\n      注意：为了防止被识别为垃圾邮件，以下内容为自动添加，同时供您查看！\n      借阅该书的人还借了什么书：\n{}\n{}\n{}\n{}\n{}\n{}\n{}'''.format(title,day,deadline,item_url,rec[0],rec[1],rec[2],rec[3],rec[4],rec[5],rec[6]), 'plain', 'utf-8')
    msg['From'] = Header("{}请注意借书到期通知".format(name), 'utf-8')
    msg['To'] = Header("{}同学".format(name), 'utf-8')

    subject = 'hello'
    msg['Subject'] = Header(subject, 'utf-8')

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

def data1file(data):
    path = r"C:\Users\Oscar\Desktop\数据.txt"
    file = open(path, "a", encoding="utf-8")
    file.write("\n")
    file.write(str(data))
    file.close()



if __name__ == '__main__':
    """
    获取当前时间
    """
    local_time = time.strftime("%Y-%m-%d", time.localtime())  # 获取当前时间
    local_time = str(local_time)
    times = re.split(r'-', local_time)
    year = times[0]
    now_month = times[1]
    now_day = times[2]

    session = requests.Session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }

    # with open(r'E:\\1.txt') as f:
    #     names=f.readlines()
    # for name in names:

    name = input("请输入用户名：")
    password = input("密码")


    soup=login(name,password)
    base_data_list=get_data(soup)

    for base_data in base_data_list:
        deadline = base_data["deadline"] #应还时间
        title=base_data["title"]   #书名
        item_url=base_data["item_url"] #图书馆的详情页
        rec=base_data["rec"]
        yinghuan_time_list = deadline.split("-")

        yinghuan_month = yinghuan_time_list[1]
        yinghuan_day = yinghuan_time_list[2]
        data_all={
                    "deadline":deadline,
                    "title":title,
                    "item_url":item_url,
                    "name":name,
                    "rec":rec
        }

        data1file(data_all)

        if int(now_month) == int(yinghuan_month) - 1:
            day = 30 - int(now_day) + int(yinghuan_day)
            if day < 20:
                send_email('202739494@qq.com',deadline,title,item_url, day,name,rec)
        elif now_month == yinghuan_month:
            day = int(yinghuan_day) - int(now_day)
            if day < 20:
                send_email('202739494@qq.com',deadline,title,item_url, day,name,rec)
                        # time.sleep(120)


