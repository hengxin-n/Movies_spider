# -*- coding: utf-8 -*-
# @Time : 2022/5/20 6:51
# @Author : Answer
# @FileName : PyCharm

# 1.准备工作,安装第三方库
import sqlite3

from bs4 import BeautifulSoup  # 网页解析,提取指定数据
import re  # 正则表达式,进行文字匹配
import urllib.request  # 指定url,获取网页数据
import urllib.error    #同上
import xlwt  # 进行excel操作

def main():  # 主函数
    baseurl = 'https://movie.douban.com/top250?start='  # url:  要爬取的网页地址也就是网址
    # 获取数据
    datalist = getData(baseurl)
    savepath = '豆瓣电影Top250.xls' # 生成一个excel文件,将数据保存到里面
    dbpath = 'movie.db'
    # 调用一下保存数据
    saveDate(datalist,savepath)
    saveData2DB(datalist,dbpath)
    # askURL('https://movie.douban.com/top250?start=')


#电影详情链接的规则
findlink = re.compile(r'<a href="(.*?)">')#创建正则表达式对象,表示规则(字符串的模式)    r:忽视所有特殊符号(比如超链接里的//)
                     #  .表示0个字符  *表示多个字符  ?表示0次或1次
#电影图片的链接
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S) #.表示0个字符  *表示0个或多个字符      re.S：让换行符包含在字符中
#电影片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
#电影的评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
#电影评价人数
findJudge =re.compile(r'<span>(\d*)人评价</span>')    #(\d*):表示数字
#电影概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
#电影的相关内容
findBd = re.compile(r'<p class="">(.*?)</p>',re.S)                                     #re.S:作用同上


# 2.爬取网页,获取数据
def getData(baseurl):
    datalist = []               #定义一个空列表
    for i in range(0, 10):      #调用获取页面信息的函数10次
        url = baseurl + str(i * 25)
        html = askURL(url)  #保存获取到的网页源码

#3.逐一解析数据(边爬取,边解析)
        soup = BeautifulSoup(html,'html.parser')
        for item in soup.find_all('div',class_="item"):             #查找符合要求的字符串,形成列表
            # print(item)  测试:查看电影item全部信息
            data = []  #保存一部电影的全部信息
            item = str(item)

            #获取电影的详情链接
            link = re.findall(findlink,item)[0]  #re库用来通过正则表达式查找指定的字符串     findlink是一个变量:在第21行代码正则表达式规则
            data.append(link)   #将电影链接追加到data列表中

            imgSrc = re.findall(findImgSrc,item)[0]
            data.append(imgSrc)     #将电影图片链接追加到data列表中

            titles = re.findall(findTitle,item)        #可能只有有一个中文名或者只有一个英文名,也可能都有
            # data.append(titles)      #将电影标题追加到data列表中
            if (len(titles) == 2):
                ctitle = titles[0]           #ctitle:中文名
                data.append(ctitle)          #添加中文名
                otitle = titles[1].replace('/','') #replace的作用:去掉无关的符号     otitle:英文名

                data.append(otitle.strip())          #添加英文名
            else:
                data.append(titles[0])
                data.append('')  #英文名字留空

            rating = re.findall(findRating,item)[0]
            data.append(rating.strip())                          #添加电影评分

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum.strip())                         #添加电影评价人数

            inq = re.findall(findInq,item)
            #电影概况可能不存在
            if len(inq) != 0:
                inq = inq[0].replace("。","")              #去掉句号
                data.append(inq.strip())                               #添加电影概况
            else:
                data.append("")                          #留空

            bd = re.findall(findBd,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?',"",bd)                              #去掉<br/>
            bd = re.sub('/','',bd)                                              #将/替换成空格
            data.append(bd.strip())                             #去掉前后的空格

            datalist.append(data)        #把处理好的一部电影信息放入到datalist中
            # print(link)
    # print(datalist)
    return datalist


# 得到指定一个url的网页内容
def askURL(url):
    # 模拟浏览器头部信息,向豆瓣发送消息
    headers = {
        'Host': 'movie.douban.com',
        'sec - ch - ua': '''" Not A;Brand";
            v = "99", "Chromium"
            v = "101", "Google Chrome"
            v = "101"''',
        'sec - ch - ua - mobile': '?0',
        'sec - ch - ua - platform': '"Windows"',
        'Sec - Fetch - Mode': 'navigate',
        'Sec - Fetch - Site': 'none',
        'Upgrade - Insecure - Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'

    }  # 用户代理,表示告诉豆瓣服务器,我们是什么类型的浏览器(本质上是告诉浏览器我们可以接受什么水平的文件内容)
    requests = urllib.request.Request(url, headers=headers)  # 封装信息
    html = ''
    # 这里可能会出现错误,用try...expect进行异常捕获(异常处理)
    try:
        response = urllib.request.urlopen(requests)  # 发送请求,返回一个response对象
        html = response.read().decode('utf-8')  # 将数据读取出来
        # print(html)
    # 异常捕获
    except urllib.error.URLError as e:  # 在爬取过程中,可能会遇到404所以要进行异常捕获
        if hasattr(e, 'code'):
            print(e.code)
        if hasattr(e, 'reason'):  # 分析为什么捕获异常没有成功
            print(e.reason)

    return html #返回得到的数据


# 4.保存数据
def saveDate(datalist,savepath):
    print('save...')
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)    #创建workbook对象
    sheet = book.add_sheet('豆瓣电影Top250',cell_overwrite_ok=True)       #创建工作表          cell_overwrite_ok:覆盖以前内容
    col = ("电影详情链接","图片链接","电影中文名","电影英文名","评分","评价人数","概况","相关信息")                  #列
    for i in range(0,8):        #将列名写进去
        sheet.write(0,i,col[i])  #列名
    for i in range(0,250):
        print('第%d条保存成功!'%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])     #数据

    book.save(savepath)             #保存


def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            if index ==4 or index ==5:
                continue
            data[index] = '"'+data[index]+'"'
        sql = '''
                insert into movie250(
                info_link,pic_link,cname,ename,score,rated,instroduction,info)
                values(%s)'''%",".join(data)
        print(sql.encode('utf-8'))
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()





#创建并初始化数据库
def init_db(dbpath):
    sql = '''
        create table movie250
        (
        id integer primary key autoincrement,
        info_link text,
        pic_link text,
        cname varchar,
        ename varchar,
        score numeric,
        rated numeric,
        instroduction text,
        info text
        )
    '''   #创建数据表
    coon = sqlite3.connect(dbpath)       #如果存在就是连接,如果不存在就是创建
    cursor = coon.cursor()
    cursor.execute(sql)
    coon.commit()  #提交
    coon.close()  #关闭数据库



if __name__ == '__main__':  # 当程序执行时
    '''调用函数'''
    main()
    # init_db('movietest.db')
    print('爬取完毕!!!')
