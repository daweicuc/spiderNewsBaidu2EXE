import urllib
import datetime
import requests
import time
import pandas as pd
import requests as req
import re
import urllib.request
from bs4 import BeautifulSoup
DBUG   = 0
reBODY =re.compile( r'<body.*?>([\s\S]*?)<\/body>', re.I)
reCOMM = r'<!--.*?-->'
reTRIM = r'<{0}.*?>([\s\S]*?)<\/{0}>'
reTAG  = r'<[\s\S]*?>|[ \t\r\f\v]'

reIMG  = re.compile(r'<img[\s\S]*?src=[\'|"]([\s\S]*?)[\'|"][\s\S]*?>')

class Extractor():
    def __init__(self, url = "", blockSize=3, timeout=30, image=False):
        self.url       = url
        self.blockSize = blockSize
        self.timeout   = timeout
        self.saveImage = image
        self.rawPage   = ""
        self.ctexts    = []
        self.cblocks   = []


    def getRawPage(self):

        try:
            header = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"}
            resp = req.get(self.url, headers=header,timeout=self.timeout)
            #print(resp.text)
            #re_text = resp.text
        except Exception as e:
            raise e
            #print(e)

        if DBUG: print(resp.encoding)
        # print(resp.encoding)
        #print(resp.text)
        #print(soup)
        if resp.encoding == 'ISO-8859-1':

            try:
                #re_text = resp.text.encode('iso-8859-1').decode('utf-8')
                re_text = resp.text.encode('iso-8859-1').decode('utf-8')
                #print(re_text)

            except Exception as e:
                    # print(e)
                    resp.encoding = "gb2312"
                    re_text = resp.text

        else:re_text = resp.text

        # print(resp.status_code)
        #print(re_text)

        return resp.status_code, re_text

    def processTags(self):
        self.body = re.sub(reCOMM, "", self.body)
        #print(self.body)
        self.body = re.sub(reTRIM.format("script"), "" ,re.sub(reTRIM.format("style"), "", self.body))
        # self.body = re.sub(r"[\n]+","\n", re.sub(reTAG, "", self.body))
        self.body = re.sub(reTAG, "", self.body)
        #print(self.body)

    def processBlocks(self):
        self.ctexts   = self.body.split("\n")
        #print(len(self.ctexts))
        #print(self.ctexts)
        self.textLens = [len(text) for text in self.ctexts]
        #print(self.textLens)
        if len(self.ctexts)<=3:
            result=self.ctexts
        else:
            #print('dd')
            self.cblocks  = [0]*(len(self.ctexts) - self.blockSize - 1)
            lines = len(self.ctexts)
            for i in range(self.blockSize):
                self.cblocks = list(map(lambda x,y: x+y, self.textLens[i : lines-1-self.blockSize+i], self.cblocks))
                #print(self.cblocks)

            maxTextLen = max(self.cblocks)

            if DBUG: print(maxTextLen)

            self.start = self.end = self.cblocks.index(maxTextLen)
            # print(self.end)
            # print(min(self.textLens))
            # print(self.cblocks[self.end])
            while self.start > 0 and self.cblocks[self.start] > min(self.textLens):
                self.start -= 1
            while self.end < lines - self.blockSize and self.cblocks[self.end] > min(self.textLens):
                self.end += 1

            result="".join(self.ctexts[self.start:self.end])
        #return "".join(self.ctexts[self.start:self.end])
        return result

    def processImages(self):
        self.body = reIMG.sub(r'{{\1}}', self.body)

    def getContext(self):
        code, self.rawPage = self.getRawPage()
        #print(self.rawPage)
        #print(self.body)
        #print(reBODY)
        #print(re.match(reBODY,self.rawPage))
        self.body = re.findall(reBODY, self.rawPage)[0]
        #print(self.body)

        if DBUG: print(code, self.rawPage)

        if self.saveImage:
            self.processImages()
        self.processTags()
        return self.processBlocks()
        # print(len(self.body.strip("\n")))


class CollectData():
    def __init__(self):
        self.new_title = []
        self.new_time=[]
        self.new_from=[]
        self.new_time_Date=[]
        self.new_content=[]
        self.target_all_url = []
        #self.keyword1=keyword1
        print("心系联通！")
        print("程序正在执行，请等候！！！")

    def get_data(self,url):
        # target_url=[]
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"}
        reponse = requests.get(url=url,
                               headers=header,
                               timeout=30
                               )
        reponse.encoding = "utf-8"
        html = reponse.text
        bf = BeautifulSoup(html, 'html5lib')
        #找出标题
        targets_url1 = bf.find_all('h3',class_="c-title")
        for target in targets_url1:
            link=target.find('a')
            self.target_all_url.append(link.get('href'))
            new_title1=link.get_text()
            self.new_title.append(new_title1.replace('\n','').replace(' ',''))

        # 找出时间和来源
        new_time_froms=bf.find_all('div',class_='c-title-author')
        for new_time_from1 in new_time_froms:
            timeAndFrom=new_time_from1.get_text().replace('\xa0','').replace('\t','')
            new_from1=timeAndFrom.split('\n')[0]
            new_time1=timeAndFrom.split('\n')[1]
            self.new_from.append(new_from1)
            self.new_time.append(new_time1)
        return self.target_all_url,self.new_title,self.new_from,self.new_time,bf

    def get_all_data(self,keyword):
        # 提取新闻第一页的内容
        #获取今天的日期
        week = datetime.datetime.now().weekday() + 1

        if (week == 1):
            yearNowWeek = datetime.datetime.now().year
            monthNowWeek = datetime.datetime.now().month
            dayNowWeek = datetime.datetime.now().day
            date_ = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
            year1 = re.findall(r'^\d+', date_)
            yearLastWeek = year1[0]
            month1 = re.findall(r'-\d+-', date_)
            monthLastWeek = month1[0].replace('-', '')
            day1 = re.findall(r'-\d+', date_)
            dayLastWeek = day1[1].replace('-', '')
            # 上周一的时间戳
            day1 = datetime.datetime.today().date() - datetime.timedelta(days=7)
            t7 = int(time.mktime(time.strptime(str(day1), '%Y-%m-%d')))
            # 本周一时间戳
            tt = datetime.datetime.now().timetuple()
            unix_ts = time.mktime(tt)
            t1 = int(unix_ts - tt.tm_hour * 60 * 60 - tt.tm_min * 60 - tt.tm_sec - 1)
        else:
            # year = datetime.datetime.now().year
            # month = datetime.datetime.now().month
            # day = datetime.datetime.now().day
            day_ = week - 1
            # print(type(day_))
            date1 = (datetime.datetime.now() - datetime.timedelta(days=day_)).strftime("%Y-%m-%d %H:%M")
            year1 = re.findall(r'^\d+', date1)
            yearNowWeek = year1[0]
            month1 = re.findall(r'-\d+-', date1)
            monthNowWeek = month1[0].replace('-', '')
            day1 = re.findall(r'-\d+', date1)
            dayNowWeek = day1[1].replace('-', '')

            date2 = (datetime.datetime.now() - datetime.timedelta(days=day_ + 7)).strftime("%Y-%m-%d %H:%M")
            year1 = re.findall(r'^\d+', date2)
            yearLastWeek = year1[0]
            month1 = re.findall(r'-\d+-', date2)
            monthLastWeek = month1[0].replace('-', '')
            day1 = re.findall(r'-\d+', date2)
            dayLastWeek = day1[1].replace('-', '')

            # 上周一的时间戳
            day1 = datetime.datetime.today().date() - datetime.timedelta(days=day_ + 7)
            t7 = int(time.mktime(time.strptime(str(day1), '%Y-%m-%d')))
            # 本周一时间戳
            day1 = datetime.datetime.today().date() - datetime.timedelta(days=day_)
            t1 = int(time.mktime(time.strptime(str(day1), '%Y-%m-%d')) - 1)
            # print(yearNowWeek, monthNowWeek, dayNowWeek, yearLastWeek, monthLastWeek, dayLastWeek, t7, t1)

        # url分析思路在txt文档中
        # url='http://news.baidu.com/ns?from=news&cl=2&bt=0&y0='+str(year)+'&m0='+str(month)+'&d0='+'&y1='+str(year)+'&m1='+str(month)+'&d1='+str(day)+'&et=0&q1='+urllib.parse.quote(keyword)+'&submit=%E7%99%BE%E5%BA%A6%E4%B8%80%E4%B8%8B&q3=&q4=&s=1&mt=24&lm=24&begin_date='+str(year)+'-'+str(month)+'-'+str(day)+'&end_date='+str(year)+'-'+str(month)+'-'+str(day)+'&tn=newstitledy&ct1=0&ct=0&rn=50&q6='
        # print(str(month),str(year),str(day),keyword)
        # url = 'http://news.baidu.com/ns?from=news&cl=2&bt=0&y0=' + str(year) + '&m0=' + str(
        #     month) + '&d0=' + '&y1=' + str(year) + '&m1=' + str(month) + '&d1=' + str(
        #     day) + '&et=0&q1=' + urllib.parse.quote(keyword) + '&submit=百度一下&q3=&q4=&s=1&mt=24&lm=24&begin_date=' + str(
        #     year) + '-' + str(month) + '-' + str(day) + '&end_date=' + str(year) + '-' + str(month) + '-' + str(day) + '&tn=newstitledy&ct1=0&ct=0&rn=50&q6='
        url='http://news.baidu.com/ns?from=news&cl=2&bt='+str(t7)+'&y0='+str(yearLastWeek)+'&m0='+str(monthLastWeek)+'&d0='+str(dayLastWeek)+\
            '&y1='+str(yearNowWeek)+'&m1='+str(monthNowWeek)+'&d1='+str(dayNowWeek)+'&et='+str(t1)+'&q1='+urllib.parse.quote(keyword)+\
            '&submit=百度一下&q3=&q4=&mt=0&lm=&s=2&begin_date=' +str(yearLastWeek) + '-' + str(monthLastWeek) + '-' + str(dayLastWeek) + '&end_date=' + str(yearNowWeek) + '-' + str(monthNowWeek) + '-' + str(dayNowWeek) +'&tn=newstitledy&ct=0&rn=50&q6='
        self.target_all_url,self.new_title,self.new_from,self.new_time,bf=self.get_data(url)
        # 提取新闻第二页及以后的内容
        page_url=bf.find_all(class_="n")
        c = re.findall(r'rsv_page=1', str(page_url))
        page_number = 50
        while len(c)!=0:
            # url = 'http://news.baidu.com/ns?word=' + urllib.parse.quote(keyword) + '&pn=' + str(page_number) + '&cl=2&ct=0&tn=newstitledy&rn=50&ie=utf-8&bt=0&et=0&lm=24'
            url = 'https://news.baidu.com/ns?word=title%3A%28' + urllib.parse.quote(keyword) + '%29&pn='+str(page_number)+'&cl=2&ct=0&tn=newstitledy&rn=50&ie=utf-8&bt='+str(t7)+'&et='+str(t1)
            self.target_all_url, self.new_title, self.new_from, self.new_time,bf = self.get_data(url)
            page_number += 50
            page_url=bf.find_all(class_="n")
            c=re.findall(r'rsv_page=1',str(page_url))
        # 提取新闻正文
        for each_url in self.target_all_url:
            try:
                self.new_content.append(Extractor(url=each_url, blockSize=5, image=False).getContext())
            except Exception as e:
                print(e)
                self.new_content.append("None")
        self.new_time_Date=self.changeTime(self.new_time)
        self.to_excel(keyword+'+'+str(yearNowWeek)+'-'+str(monthNowWeek)+'-'+str(dayNowWeek)+'.xls')

    def changeTime(self,new_time):
        time1 = []
        for time in new_time:
            if len(re.findall(r'[0-9]+分钟前', time)) != 0:
                t = re.findall(r'[0-9]+', time)
                time1.append((datetime.datetime.now() - datetime.timedelta(minutes=int(t[0]))).strftime("%Y-%m-%d %H:%M"))
                # print((datetime.datetime.now() - datetime.timedelta(minutes=int(t[0]))).strftime("%Y-%m-%d %H:%M"))
            elif len(re.findall(r'[0-9]+小时前', time)) != 0:
                h = re.findall(r'[0-9]+', time)
                time1.append((datetime.datetime.now() - datetime.timedelta(hours=int(h[0]))).strftime("%Y-%m-%d %H:%M"))
                # print((datetime.datetime.now() - datetime.timedelta(hours=int(h[0]))).strftime("%Y-%m-%d %H:%M"))
            else:
                y = re.findall(r'[0-9]+年', time)
                y1 = re.findall(r'[0-9]+', y[0])
                m = re.findall(r'[0-9]+月', time)
                m1 = re.findall(r'[0-9]+', m[0])
                d = re.findall(r'[0-9]+日', time)
                d1 = re.findall(r'[0-9]+', d[0])
                mi = re.findall(r'[0-9]+:', time)
                mi1 = re.findall(r'[0-9]+', mi[0])
                s = re.findall(r':[0-9]+', time)
                s1 = re.findall(r'[0-9]+', s[0])
                t = y1[0] + "-" + m1[0] + "-" + d1[0] + " " + mi1[0] + ":" + s1[0]
                time1.append(t)
        return time1
# 存到excel表中
    def to_excel(self, excel_path):
        news_dict = {'新闻标题': self.new_title, '新闻来源网站': self.new_from, '发稿时间': self.new_time_Date,
                     '新闻链接': self.target_all_url, '新闻正文': self.new_content}
        news_df = pd.DataFrame(news_dict)
        excel_writer = pd.ExcelWriter(excel_path)
        news_df.to_excel(excel_writer, index=False)
        excel_writer.save()
    # 自启动
    def timing(self,keyword):
        while True:
            now=datetime.datetime.now()
            if now.hour==9 and now.minute==5:
                break
            time.sleep(20)
        self.get_all_data(keyword)
        time.sleep(300)

if __name__ == "__main__":
    start = time.clock()
    print('本执行文件主要是查询百度新闻！')
    print('查询时间是上周一00:00:00——上周日的23:59:59(时:分:秒)！')
    print('查询结果保存在excel中,命名格式为：关键词+本周一时间（年月日）！')
    keyword = input("请输入查询的关键词：")
    # hour=input("请输入自启动时间（0-24）:")
    newData = CollectData()
    newData.get_all_data(keyword)
    end = time.clock()
    print('程序执行了：%ds' % (end - start))
    print(input("程序结束！"))