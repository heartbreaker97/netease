
from neteaseSpider.proxy.parsing_html import *
from neteaseSpider.proxy.checking_ip import *

def main():

    ipPoolsPath = "ipProxy/ip_pools.txt"                 # 原始ip保存路径
    ipFormatPoolsPath = "ipProxy/ipFormatPools.txt"    # 格式化后ip保存路径
    ipUsePath = "ipProxy/ipUse.txt"                     # 可用ip保存路径

    openProxy = False  # 是否要开启代理模式
    if not openProxy:
        # 不开启代理模式，直接获取代理ip
        get_data5u_free_ip(None, ipPoolsPath, openProxy)
        get_kuaidaili_free_ip(None, ipPoolsPath, openProxy)
        get_xsdaili_free_ip(None, ipPoolsPath, openProxy)
        get_xicidaili_free_ip(None, ipPoolsPath, openProxy)
        get_89ip_free_ip(None, ipPoolsPath, openProxy)
    else:
        # 开启代理模式，获取代理ip
        available_ip_path = "ipProxy/ipUse.txt"  # 目前可用的代理ip的保存路径
        ipUseList = []
        with open(available_ip_path, "r") as fr:
            ipUseLines = fr.readlines()
            for ipUse_line in ipUseLines:
                ipUseLineNew = ipUse_line.replace("\n", "")
                ipUseList.append(ipUseLineNew)
        for i in range(len(ipUseList)):
            # 获取ip建立IP池
            try:
                print("正在使用第" + str(i) + "条代理ip")
                get_data5u_free_ip(ipUseList[i], ipPoolsPath, openProxy)
                break
            except:
                pass
        for i in range(len(ipUseList)):
            # 获取ip建立IP池
            try:
                print("正在使用第" + str(i) + "条代理ip")

                get_kuaidaili_free_ip(ipUseList[i], ipPoolsPath, openProxy)
                break
            except:
                pass
        for i in range(len(ipUseList)):
            # 获取ip建立IP池
            try:
                print("正在使用第" + str(i) + "条代理ip")
                get_xsdaili_free_ip(ipUseList[i], ipPoolsPath, openProxy)
                break
            except:
                pass
        for i in range(len(ipUseList)):
            # 获取ip建立IP池
            try:
                print("正在使用第" + str(i) + "条代理ip")
                get_xicidaili_free_ip(ipUseList[i], ipPoolsPath, openProxy)
                break
            except:
                pass
        for i in range(len(ipUseList)):
            # 获取ip建立IP池
            try:
                print("正在使用第" + str(i) + "条代理ip")
                get_89ip_free_ip(ipUseList[i], ipPoolsPath, openProxy)
                break
            except:
                pass
    # 筛选ip进行查重
    ip_format(ipPoolsPath, ipFormatPoolsPath)
    check_repeat(ipFormatPoolsPath)
    # 验证ip可用性
    ip_batch_inspection(ipFormatPoolsPath, ipUsePath)


if __name__ == '__main__':
    main()