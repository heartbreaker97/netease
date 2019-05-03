# -*- coding: utf-8 -*-
import requests
import re
import math
import threadpool
import random
import time
import threading
from neteaseSpider.utils.Log import Log
from neteaseSpider.utils.Lib import formatTime
from neteaseSpider.utils.File import saveFile, readFile
from neteaseSpider.utils.Decrypt import Decrypt
from neteaseSpider.utils.Agent import FakeUserAgent



class Spider:

    """
    爬虫
    """
    #初始化id
    def __init__(self):
        self.userName = userName
        self.uid = self.getUid(self.userName)
        #听歌记录以及歌单歌曲
        self.songList = []
        self.commentId = []
        #歌的总数
        self.songLeng = 0

    # 发送http请求,提交方式为post
    def sendHttpByPost(self, url, msg):
        #获得两个加密后的字符r
        dcpt = Decrypt(msg)
        params, encSecKey = dcpt.getParams()
        data = {'params': params, 'encSecKey': encSecKey}
        #随机代理ip
        proxy = {"http": ipProxy[random.randint(0, proxyNum-1)]}
        #Log.w('现在用的代理IP是' + str(proxy))
        try:
            #随机用户头
            headers = fakeUserAgent.random_headers()
            r = requests.post(url, headers=headers, data=data, proxies=proxy)
            #time.sleep(1)
            r.encoding = "utf-8"
            if r.status_code == 200:
                # 返回json格式的数据
                return r.json()
            else:
                return r.status_code
        except Exception as e:
            Log.e('发送http请求失败，错误信息为：' + str(e))


    # 得到用户id
    def getUid(self, username):
        # 根据用户名获取用户信息的api
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        msg = '{"s":"' + username + '","type":"1002","offset":"0","total":"true","limit":"100","csrf_token":""}'
        r = self.sendHttpByPost(url, msg)
        users = r['result']['userprofiles']
        # 从名字相似的人中找出指定用户的
        for user in users:
            if user['nickname'] == username:
                return user['userId']

    #得到听歌记录的id
    def getRecodeList(self):
        #听歌记录的api
        url = 'https://music.163.com/weapi/v1/play/record?csrf_token='
        msg = '{"uid":"' + str(self.uid) + '","type":"-1","offset":"0","total":"true","limit":"1000","csrf_token":""}'
        r = self.sendHttpByPost(url, msg)
        #如果无求访问返回0
        if r['code'] == -2:
            Log.w("无权访问 "+ self.userName +" 的听歌记录")
            return 0
        #将听歌记录id加到歌曲列表
        if r['code'] == 200:
            Log.v("获取 "+ self.userName +" 的听歌记录排行榜成功"+'\n')
            totalData = []
            totalData.append(r['weekData'])
            totalData.append(r['allData'])
            Log.d('正在获得 '+ self.userName +' 的听歌排行榜的歌曲信息')
            for records in totalData:
                if records is not None:
                    for data in records:
                        songId = data['song']['song']['id']
                        songName = data['song']['song']['name']
                        #不重复歌曲
                        if songId not in self.songList:
                            self.songList.append(([songId , songName], None))
            Log.v('已获得 '+ self.userName +' 的听歌排行榜的歌曲信息'+'\n')

    #获得取单歌曲
    def getPlayList(self):
        url = 'https://music.163.com/weapi/user/playlist?csrf_token='
        msg = '{"uid":"' + str(self.uid) + '","wordwrap":"7","offset":"0","total":"true","limit":"100","csrf_token":""}'
        r = self.sendHttpByPost(url, msg)
        playLists = r['playlist']
        listId = []
        for playList in playLists:
            #只看自己创建的歌单
            if playList['userId'] == self.uid:
                listId.append([ playList['id'], playList['name'] ])
            #因为是按序排的，自己创建下面的就是收藏
            else:
                break
        Log.v('已获得 '+ self.userName +' 的歌单信息' + '\n')
        self.getSongByList(listId)

    #根据歌单获得歌曲
    def getSongByList(self,listIds):
        for listId in listIds:
            Log.d('正在获得歌单《' + listId[1] + '》的歌曲信息')
            url = 'https://music.163.com/playlist?id={}'.format(listId[0])
            # 随机用户头
            headers = fakeUserAgent.random_headers()
            res = requests.get(url, headers=headers)
            #正则匹配出歌曲id
            songIds = re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>', res.text)
            for songId in songIds:
                # 不重复歌曲
                if songId not in self.songList:
                    #tmp = []
                    #tmp.append([songId[0],songId[1]])
                    self.songList.append(([songId[0],songId[1]], None))
            Log.v('已获得歌单《' + listId[1] + '》的全部歌曲信息' + '\n')

    #获得歌曲评论
    def getComments(self):
        songList = self.songList
        #开启多线程爬取歌曲评论
        pool_size = 15
        pool = threadpool.ThreadPool(pool_size)
        # 创建工作请求，这里他自己会把list分开
        reqs = threadpool.makeRequests(self.getDatas, songList)
        # 将工作请求放入队列
        [pool.putRequest(req) for req in reqs]
        pool.wait()


    def getData(self, song):
        self.getDatas(song[0], song[1])

    #单线程实现
    def getDatas(self, sid, sname):
        #sname = '静夜的但'
        #sid = '299039'

        Log.d('正在爬取歌曲《' + sname + '》的评论')
        page = 1
        url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(sid) + '?csrf_token='
        msg = '{"rid":"R_SO_4_' + str(sid) + '","offset":"0","total":"false","limit":"20","csrf_token":""}'
        # 获取第一页评论
        r = self.sendHttpByPost(url, msg)

        # 评论总数
        total = r['total']
        # 总页数a
        pages = math.ceil(total / 20)

        # 开始获取歌曲的全部评论
        # 只得到前1000条评论就是了
        while page <= pages  and page <= 50:
            Log.d('正在爬取歌曲《' + sname + '》的第 ' + str(page) + ' 页评论')
            offset = (page - 1) * 20
            # offset和limit是必选参数,其他参数是可选的,其他参数不影响data数据的生成
            msg = '{"offset":' + str(offset) + ',"total":"True","limit":"100","csrf_token":""}'
            url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(sid) + '?csrf_token='
            r = self.sendHttpByPost(url, msg)
            # 从第二页开始获取评论
            for comment in r['comments']:
                if comment['user']['userId'] == self.uid:
                    #解决目前无法找出原因的使用多线程会重复打印评论问题
                    if comment['commentId'] not in self.commentId:
                        self.commentId.append(comment['commentId'])
                    else:
                        continue
                    # 将爬取信息写入
                    #mutexFile.acquire()
                    self.write(comment, sname)
                    #mutexFile.release()
            page += 1
        Log.v('爬取结束歌曲《' + sname + '》的评论' + '\n')
        global process
        process += 1
        Log.v('当前进度为: ' + str(process) + '/' + str(self.songLeng))

    #写入txt文件
    def write(self, comment, songname):
        #互斥写文件
        #mutexFile.acquire()
        data = self.userName + '在 ' +  str(formatTime(comment['time'] / 1000)) + '的时候在\n' + '《' + songname + '》' + '下评论了“' + comment['content'] + '”\n\n'
        print(data)
        saveFile(fileName, data)
        #mutexFile.release()

    #开始爬数据
    def start(self):
        #获得听歌记录歌曲
        self.getRecodeList()
        #获得歌单中歌曲
        self.getPlayList()
        self.songLeng = len(self.songList)
        Log.d('共有 %d 首歌，预计需要 %d 小时 %d 分钟' % (self.songLeng, self.songLeng / 60, self.songLeng % 60))
        #获得歌曲评论
        self.getComments()



if __name__ == '__main__':
    # 设置用户名
    userName = input("请输入用户名：")
    # 设置文件userName
    fileName = userName + ".txt"
    # 设置未爬取信息
    wrongFile = userName + "未爬到歌曲.txt"
    #写文件互斥锁
    mutexFile = threading.Lock()
    #假用户请求头
    fakeUserAgent = FakeUserAgent()
    #进度
    process = 0
    # 获得代理ip
    ipProxy = readFile("../proxy/ipProxy/ipUse.txt")
    proxyNum = len(ipProxy)
    lickDog = Spider()
    lickDog.start()


