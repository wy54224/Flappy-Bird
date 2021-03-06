#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import socket, json, base64
import sys
import rsa 
reload(sys)
sys.setdefaultencoding('utf-8')

# constants
TIMEOUT = -1
CLOSED = -2
EMPTY = -3    #means read empty data

# param: sock, dict
# return: 1-success TIMEOUT-timeout CLOSED-closed EMPTY-empty
def send(sock, dic):  # take dict as argument!!
    try:
        sock.send(pack(dic))
    except socket.error as (err_code, err_message):
        if err_code == 9:
            return CLOSED
        else:
            return TIMEOUT
    return 1

# param: sock
# return: table-success TIMEOUT-timeout CLOSED-closed EMPTY-empty
def read(sock):
    #读取三位的长度信息
    sock.setblocking(0)
    try:
        length = sock.recv(3)
    except socket.error as (err_code, err_message):
        #异常处理
        if err_code == 35:
            return TIMEOUT
        elif err_code == 54:
            return CLOSED
        elif err_code == 9:
            return CLOSED
        else:
            return TIMEOUT
    #读取到''说明socket另一头被关闭
    if length == '':
        return CLOSED
    
    length = int(length)
    if length == 0:
        return EMPTY
    
    #根据长度信息读取数据
    try:
        data = sock.recv(length)
    except socket.error as (err_code, err_message):
        #异常处理
        if err_code == 35:
            return TIMEOUT
        elif err_code == 54:
            return CLOSED
        elif err_code == 9:
            return CLOSED
        else:
            return TIMEOUT
    #读取到''说明socket另一头被关闭
    if data == '':
        return CLOSED
    
    #解析数据
    return unpack(data)

# 功能：对输入的dict使用json转换 使用base64加密 加上长度信息
# 输入：dict
# 输出：string
def pack(dic):
    # 转换成json
    jsonData = json.dumps(dic)
    # base64加密
    jsonData = base64.b64encode(jsonData)
    # 加上头部信息
    length = len(jsonData)
    string = None
    if length < 10 and length > 0:
        string = "00"+str(length)+jsonData
    elif length < 100:
        string = "0"+str(length)+jsonData
    elif length < 1000:
        string = str(length)+jsonData
    else:
        string = "000"
    return string
    
# 功能：对输入的string（不含长度信息） 先进行rsa解密 进行base64解密 再用json转换 得到dict
# 输入string
# 输出dict
def unpack(string):
    # rsa解密
    prikey = readPrivateKey()
    string = rsa_decrypt(string, prikey)
    # base64解密
    jsonData = base64.b64decode(string)
    # json解析
    dic = json.loads(jsonData)
    return dic

#对string进行rsa解密，_pri为私钥
def rsa_decrypt(biz_content, _pri):
    biz_content = base64.b64decode(biz_content.encode('utf-8'))
    # 1024bit key
    default_length = 128
    len_content = len(biz_content)
    if len_content < default_length:
        return rsa.decrypt(biz_content, _pri)
    offset = 0
    params_lst = []
    while len_content - offset > 0:
        if len_content - offset > default_length:
            params_lst.append(rsa.decrypt(biz_content[offset: offset+default_length], _pri))
        else:
            params_lst.append(rsa.decrypt(biz_content[offset:], _pri))
        offset += default_length
    target = ''.join(params_lst)
    return target
    
def readPrivateKey():
    with open('private.pem') as privatefile:
        p = privatefile.read()
        prikey = rsa.PrivateKey.load_pkcs1(p)
    return prikey