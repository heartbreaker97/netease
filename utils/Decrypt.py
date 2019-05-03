import math, random
from Crypto.Cipher import AES
import base64
import codecs

class Decrypt(object):
    """
    加密信息，post数据
    """
    def __init__(self, d):
        self.d = d
        self.e = '010001'
        self.f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5a" \
                 "a76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46be" \
                 "e255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.g = '0CoJUm6Qyw8W8jud'
        self.random_text = self.getRandomStr()

    def getRandomStr(self):
        str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x in range(16):
            index = math.floor(random.random() * len(str))
            res += str[index]
        return res

    def aesEncrypt(self, text, key):
        iv = '0102030405060708'
        pad = 16 - len(text.encode()) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
        msg = base64.b64encode(encryptor.encrypt(text.encode('utf-8')))
        return msg

    def rsaEncrypt(self, value, text, modulus):
        '''进行rsa加密'''
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(value, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def getParams(self):
        params = self.aesEncrypt(self.d, self.g)
        params = self.aesEncrypt(params.decode('utf-8'), self.random_text).decode('utf-8')
        enc_sec_key = self.rsaEncrypt(self.e, self.random_text, self.f)
        return  params, enc_sec_key

if __name__ == '__main__':
    des = Decrypt('中文测试')
    params, encSeckey = des.get_data()
    print(params)
    print(encSeckey)