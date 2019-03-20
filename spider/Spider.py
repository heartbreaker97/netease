# -*- coding: utf-8 -*-
import requests
import re
import math
from neteaseSpider.utils.Log import Log
from neteaseSpider.utils.Core import get_params
from neteaseSpider.utils.Lib import formatTime
from neteaseSpider.utils.File import saveFile

#定义头
headers={
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'zh-CN,zh;q=0.9',
             'Connection': 'keep-alive',
             #'Cookie': '_iuqxldmzr_=32; _ntes_nnid=dc9235f7e53434dff2660b24fc10ade3,1552979170011; _ntes_nuid=dc9235f7e53434dff2660b24fc10ade3; WM_TID=24xZGtv9i0hERQEVRFJsx5NltTxKj4aF; WM_NI=cxGQgJx%2BUQX2OH1cggmK4NTiXAIT1802OhoWSrihaSI0V4pL4cNWnJtje6gyWjdOgiUq3ra9ODAbDSF5PFddOB%2FFmUMY0ol2CvA9AgpnBd%2BdnWlNxclIdU3rdZux0reXS1o%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb5f76a989b83b3c834f39e8ea7c54f978f8f85f761b4be8da2ce47bbe8bcafea2af0fea7c3b92aa1a889b2e642bcf59bb2db3a8d98ff84e66daf95fcafd7639c9f87b5b434f4ee8189ee5d91aea789e4598bf09ad5f348f8bd82b8ed42b8b6abd7e67395b6acb0e66397affd93e4338d9c8f83c75986eba0a7e7708d9ee1a7f05f8f870090ef3a81aa8fdac46db4b28e85aa70ae89a4affb69b097acb6b27aa886bb99b37aa7889dd2ee37e2a3; JSESSIONID-WYYY=zW0%2FOl6bsF7ieMciwNFs99s%2BNEoKOXm6BIqHrraNVWHdJGBcTnA8BMfES1W%2BrevRTnfJp3ybiY%5CHyjUQ%2BUwxlKIbMOZn7oqMkVi5uUl53hsTZa%5CuRhYQQ%5C5tNygzI3tR2i3almjEruYTmD75%2Fc1Yu%5CRN6BbljT%5CBhrKTvKlAMxUOgdY8%3A1553062003955',
             'Host': 'music.163.com',
             'Referer': 'http://music.163.com/',
             'Upgrade-Insecure-Requests': '1',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/66.0.3359.181 Safari/537.36'}


#设置用户名
userName = input("请输入用户名：")
#设置文件userName
fileName = userName + ".txt"

class Spider:

    #初始化id
    def __init__(self):
        self.userName = userName
        self.uid = self.getUid(self.userName)
        #听歌记录以及歌单歌曲
        self.songList = []

    # 发送http请求,提交方式为post
    def sendHttpByPost(self, url, msg):
        #获得两个加密后的字符
        params, encSecKey = get_params(msg)
        data = {'params': params, 'encSecKey': encSecKey}
        try:
            r = requests.post(url, headers=headers, data=data)
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
                            self.songList.append((songId , songName))
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
            res = requests.get(url, headers=headers)
            #正则匹配出歌曲id
            songIds = re.findall(r'<a href="/song\?id=(\d+)">(.*?)</a>', res.text)
            for songId in songIds:
                # 不重复歌曲
                if songId not in self.songList:
                    self.songList.append(songId)
            Log.v('已获得歌单《' + listId[1] + '》的全部歌曲信息' + '\n')

    #获得歌曲评论
    def getComments(self):

        # 文件存储路径
        #filepath =
        for songId in self.songList:
            Log.d('正在爬取歌曲《'+ songId[1] +'》的评论')
            flag = True
            page = 1
            url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songId[0]) + '?csrf_token='
            msg =  '{"rid":"R_SO_4_' + str(songId[0]) + '","offset":"0","total":"false","limit":"20","csrf_token":""}'
            # 获取第一页评论
            r = self.sendHttpByPost(url, msg)
            # 评论总数
            total = r['total']
            # 总页数
            pages = math.ceil(total / 20)

            # 开始获取歌曲的全部评论
            #一般一首歌只会评论一次，如果获取到一条评论结束flag
            while page <= pages and flag and page <= 50:
                Log.d('正在爬取歌曲《' + songId[1] + '》的第 ' + str(page) +' 页评论')
                offset = (page - 1) * 20
                # offset和limit是必选参数,其他参数是可选的,其他参数不影响data数据的生成
                msg = '{"offset":' + str(offset) + ',"total":"True","limit":"100","csrf_token":""}'
                url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songId[0]) + '?csrf_token='
                r = self.sendHttpByPost(url, msg)
                # 从第二页开始获取评论
                for comment in r['comments']:
                    if comment['user']['userId'] == self.uid:
                        #将爬取信息写入
                        self.write(comment, songId[1])
                        flag = False
                page += 1
            Log.v('已爬取到歌曲《'+ songId[1] +'》的评论' + '\n')

    def write(self, comment, songname):
        data = self.userName + '在 ' +  str(formatTime(comment['time'] / 1000)) + '的时候在\n' + '《' + songname + '》' + '下评论了“' + comment['content'] + '”\n\n'
        print(data)
        saveFile(fileName, data)

    #开始爬数据
    def start(self):
        #获得听歌记录歌曲
        self.getRecodeList()
        #获得歌单中歌曲
        self.getPlayList()
        #获得歌曲评论
        self.getComments()



if __name__ == '__main__':
    lickDog = Spider()
    lickDog.start()
    #print(formatTime(time.daylight()))

