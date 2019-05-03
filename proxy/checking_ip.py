import requests
import time
import threadpool
import json
from neteaseSpider.utils.File import saveFile


ip_use_path = "ipProxy/ipUse.txt"

def check_repeat(path):
    """
    检查文件中每一行的内容是否重复，删除重复内容
    :param path: 文件路径
    :return:
    """
    try:
        # 读取文件
        data_list = []
        with open(path, "r") as fr:
            lines = fr.readlines()
            fr.close()
        for line in lines:
            data_list.append(line)
        new_data_list = list(set(data_list))    # 查重
        file_name = path.split("/")
        print(file_name[-1] + "文件共有 " + str(len(data_list)) + " 条数据")
        print("经过查重,现在共有 " + str(len(new_data_list)) + " 条数据")
        # 保存文件
        with open(path ,"w" , encoding='utf-8') as f:
            for i in range(len(new_data_list)):
                f.write(new_data_list[i])
            f.close()
            print(file_name[-1] + "文件查重成功")
    except Exception as e:
        print("文件查重失败！！！")
        print(e)


def ip_format(read_path, save_path):
    """
    将文件中的代理ip进行格式化转换，并进行查重
    :param read_path: 读取待转换的代理ip的文件路径
    :param save_path: 转换完成的代理ip的保存路径
    :return:
    """
    data_list = []
    with open(read_path, "r") as fr:
        lines = fr.readlines()
        fr.close()
    for line in lines:
        new_line = line.split("___")
        ip_format_line = new_line[0].replace(" ", "") + ":" + new_line[1] + "\n"
        data_list.append(ip_format_line)
    with open(save_path, "a") as fs:
        for i in range(len(data_list)):
            fs.write(data_list[i])
        fs.close()
        print("文件保存成功")
        fs.close()

def ip_test(proxy):
    proxy_temp = {"http": proxy}
    url = "http://httpbin.org/ip"
    #url = "http://ip.chinaz.com/getip.aspx"
    try:
        response = requests.get(url, proxies=proxy_temp, timeout=5).text
        res = json.loads(response)
        print('返回信息为: '+ res['origin'])
        testIp = proxy.split(':')[0]
        responseIp = res['origin'].split(',')[0]
        #print('代理ip返回的' + responseIp)
        #检测是否是高匿名
        if testIp == responseIp:
            return True
        else:
            re
    except Exception as e:
        return False



def ip_batch_inspection(read_path, save_path):
    """
     验证多个代理ip是否可用
    :param read_path: 代理ip文件路径
    :param save_path: 验证可用的代理ip保存路径
    :return:
    """
    with open(read_path, "r") as fr:
        lines = fr.readlines()
        fr.close()
        count = 0
        file_name = read_path.split("/")
        print(file_name[-1] + "文件共有 " + str(len(lines)) + " 条数据")
        proxies = []
        for line in lines:
            count += 1
            proxy = line.replace("\n", "")
            proxies.append(proxy)
        #for i in proxies:
        #    validation(i)
        #多线程验证
        pool_size = 15
        pool = threadpool.ThreadPool(pool_size)
        # 创建工作请求，这里他自己会把list分开
        reqs = threadpool.makeRequests(validation, proxies)
        # 将工作请求放入队列
        [pool.putRequest(req) for req in reqs]
        pool.wait()
        '''try:
        print(ip_proxies)
        isUse = ip_test(ip_proxies)  # 如果是本地ip，返回值为大于0数值
        if isUse == True:
            print('拉闸')
        if isUse == False:
            with open(save_path, "a" , encoding='utf-8') as fs:
                fs.write(ip_proxies + "\n")
            print('嘻嘻嘻嘻有效了')
    except Exception as e:
        #pass
        print("错误信息为" + str(e))
    print("验证中......%.2f%%" % (count/len(lines)*100))
print("验证完毕")'''

#验证ip的逻辑控制
def validation(ip_proxies):
    try:

        print(ip_proxies)
        isUse = ip_test(ip_proxies)  # 是否可用
        if isUse == False:
            print('拉闸')
        if isUse == True:
            with open(ip_use_path, "a", encoding='utf-8') as fs:
                fs.write(ip_proxies + "\n")
            print('嘻嘻嘻嘻有效了')
    except Exception as e:
        # pass
        print("错误信息为" + str(e))

if __name__ == '__main__':
    today = time.strftime("%Y_%m_%d")  # 当前日期
    ip_format_pools_path = "ipProxy/ipFormatPools.txt"  # 格式化后ip保存路径
    ip_use_path = "ipProxy/ipUse.txt"  # 可用ip保存路径
    ip_batch_inspection(ip_format_pools_path, ip_use_path)