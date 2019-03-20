# -*- coding: utf-8 -*-
import time
#将时间戳改成YMDHMS格式
def formatTime(tramp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tramp))