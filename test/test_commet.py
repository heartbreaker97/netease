import requests
import math
import random
# pycrypto
from Crypto.Cipher import AES
import codecs
import base64


# 构造函数获取歌手信息
def get_comments_json(url, data):
    headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'zh-CN,zh;q=0.9',
             'Connection': 'keep-alive',
             #'Cookie': '_iuqxldmzr_=3s; _ntes_nnid=dc9235f7e53434dff2660b24fc10ade3,1552979170011; _ntes_nuid=dc9235f7e53434dff2660b24fc10ade3; WM_NI=uTdV8%2Bzcmq1tfNvkiBdBMMcoQsPRaUatd3YbZe1wjAUMSoePAjXpfWtC2cV%2BjFm3ChfeJBEExZTe1Q5nV0tk%2B%2BpE2xi3l2p1a4R649vJplkzsBlLmUPiqX5AcwzAoLfmSVA%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb3c84bb2b1e1d3c66ef59a8aa2d45e828a8aaeee3cf8bda895db3ca7b7fc86d82af0fea7c3b92ab78cacb7bb21babda392b480a692ba8cec4aa89e83aee26593ada0b3e45fa3acacd4dc6a9abbff98e94b97939d90e85c83b69891e55db89dfe84d521aa9aa3d4c264a6bb86a3c84fbc869c86b45bf7b29ad1f761e9f5c0a6b174abeda4d3f33ba3ec9ed7b733b696c08dea72b19ea4adf05f94b7bfb9b84ba1a9b6a2ee48a6b39db7c437e2a3; WM_TID=24xZGtv9i0hERQEVRFJsx5NltTxKj4aF; __remember_me=true; JSESSIONID-WYYY=QW4%2FCN%2FIs0%2Bku9ieVh8sdtUqNO%5C7KaOp0xCHEJWcVWJoUojrq6x8UZrrSe7BWJZhq9fJdjnIiio0gCUhYl2xEM8OGHU00gTOVRgR3cjn3xdN%5CfeolsrQ8ef7NcqFKt%2BiIIOa%2F%2Fnf93TqCyNHlyeY6hEs6TTpIWE%5CNCfqVBJXMsODidGh%3A1552992562833; MUSIC_U=02ade4b599a7e26c4dfc7349f87e1d544d4731a629943a28ff88ec755bc90cea9e6209551583b7ffa22d0edcfa59e13e31b299d667364ed3; __csrf=4d07520447b3774e5476b9c8f65066cf',
             'Host': 'music.163.com',
             'Referer': 'http://music.163.com/',
             'Upgrade-Insecure-Requests': '1',
             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/66.0.3359.181 Safari/537.36'}

    try:
        r = requests.post(url, headers=headers, data=data)
        r.encoding = "utf-8"
        if r.status_code == 200:

            # 返回json格式的数据
            return r.json()

    except:
        print("爬取失败!")


# 生成16个随机字符
def generate_random_strs(length):
    string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    # 控制次数参数i
    i = 0
    # 初始化随机字符串
    random_strs  = ""
    while i < length:
        e = random.random() * len(string)
        # 向下取整
        e = math.floor(e)
        random_strs = random_strs + list(string)[e]
        i = i + 1
    return random_strs


# AES加密
def AESencrypt(msg, key):
    # 如果不是16的倍数则进行填充(paddiing)
    padding = 16 - len(msg) % 16
    # 这里使用padding对应的单字符进行填充
    msg = msg + padding * chr(padding)
    # 用来加密或者解密的初始向量(必须是16位)
    iv = '0102030405060708'

    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    # 加密后得到的是bytes类型的数据
    encryptedbytes = cipher.encrypt(msg.encode('utf-8'))
    # 使用Base64进行编码,返回byte字符串
    encodestrs = base64.b64encode(encryptedbytes)
    # 对byte字符串按utf-8进行解码
    enctext = encodestrs.decode('utf-8')

    return enctext


# RSA加密
def RSAencrypt(randomstrs, key, f):
    # 随机字符串逆序排列
    string = randomstrs[::-1]
    # 将随机字符串转换成byte类型数据
    text = bytes(string, 'utf-8')
    seckey = int(codecs.encode(text, encoding='hex'), 16)**int(key, 16) % int(f, 16)
    return format(seckey, 'x').zfill(256)


# 获取参数
def get_params(page):
    # msg也可以写成msg = {"offset":"页面偏移量=(页数-1) *　20", "limit":"20"},offset和limit这两个参数必须有(js)
    # limit最大值为100,当设为100时,获取第二页时,默认前一页是20个评论,也就是说第二页最新评论有80个,有20个是第一页显示的
    # msg = '{"rid":"R_SO_4_1302938992","offset":"0","total":"True","limit":"100","csrf_token":""}'
    # 偏移量
    offset = (page-1) * 20
    # offset和limit是必选参数,其他参数是可选的,其他参数不影响data数据的生成
    msg = '{"offset":' + str(offset) + ',"total":"True","limit":"20","csrf_token":""}'
    key = '0CoJUm6Qyw8W8jud'
    f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    e = '010001'
    enctext = AESencrypt(msg, key)
    # 生成长度为16的随机字符串
    i = generate_random_strs(16)

    # 两次AES加密之后得到params的值
    encText = AESencrypt(enctext, i)
    # RSA加密之后得到encSecKey的值
    encSecKey = RSAencrypt(i, e, f)
    return encText, encSecKey


def hotcomments(html, songname, i, pages, total, filepath):
    # 写入文件
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    print("正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))

    # 精彩评论
    m = 1
    # 键在字典中则返回True, 否则返回False
    if 'hotComments' in html:
        for item in html['hotComments']:
            # 提取发表热门评论的用户名
            user = item['user']
            # 写入文件
            print("热门评论{}: {} : {}    点赞次数: {}".format(m, user['nickname'], item['content'], item['likedCount']))
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write("热门评论{}: {} : {}   点赞次数: {}\n".format(m, user['nickname'], item['content'], item['likedCount']))
                # 回复评论
                if len(item['beReplied']) != 0:
                    for reply in item['beReplied']:
                        # 提取发表回复评论的用户名
                        replyuser = reply['user']
                        print("回复：{} : {}".format(replyuser['nickname'], reply['content']))
                        f.write("回复：{} : {}\n".format(replyuser['nickname'], reply['content']))
            m += 1


def comments(html, songname, i, pages, total, filepath):
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write("\n正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    print("\n正在获取歌曲{}的第{}页评论,总共有{}页{}条评论！\n".format(songname, i, pages, total))
    # 全部评论
    j = 1
    for item in html['comments']:
        # 提取发表评论的用户名
        user = item['user']
        print("全部评论{}: {} : {}    点赞次数: {}".format(j, user['nickname'], item['content'], item['likedCount']))
        with open(filepath, 'a', encoding='utf-8') as f:

            f.write("全部评论{}: {} : {}   点赞次数: {}\n".format(j, user['nickname'], item['content'], item['likedCount']))
            # 回复评论
            if len(item['beReplied']) != 0:
                for reply in item['beReplied']:
                    # 提取发表回复评论的用户名
                    replyuser = reply['user']
                    print("回复：{} : {}".format(replyuser['nickname'], reply['content']))
                    f.write("回复：{} : {}\n".format(replyuser['nickname'], reply['content']))

        j += 1


def main():

    # 歌曲id号
    songid = 38592976

    # 歌曲名字
    songname = "Dream it possible"
    # 文件存储路径
    filepath = songname + ".txt"
    page = 1
    params, encSecKey = get_params(page)
    print(params)
    print(encSecKey)
    url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(songid) + '?csrf_token='
    data = {'params': params, 'encSecKey': encSecKey}
    # url = 'https://music.163.com/#/song?id=19292984'
    # 获取第一页评论
    html = get_comments_json(url, data)
    # 评论总数
    total = html['total']
    # 总页数
    pages = math.ceil(total / 20)
    hotcomments(html, songname, page, pages, total, filepath)
    comments(html, songname, page, pages, total, filepath)

    # 开始获取歌曲的全部评论
    page = 2
    while page <= pages:

        params, encSecKey = get_params(page)
        data = {'params': params, 'encSecKey': encSecKey}
        html = get_comments_json(url, data)
        # 从第二页开始获取评论
        comments(html, songname, page, pages, total, filepath)
        page += 1


if __name__ == "__main__":
    main()