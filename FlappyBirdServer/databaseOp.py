# -*- coding: utf-8 -*-
import os
import re

#用于注册
UserHasExisted = -1
#用于登陆
NotAUser = -1
PasswordError = -2

THISDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.normpath(os.path.join(THISDIR, 'DataBase'))

def Sign_up(data):
    #get information
    data = data.strip()
    dataList = data.split('\t')
    if len(dataList) != 2:
        print("Error: sign_in data has error")
    userName = dataList[0]
    password = dataList[1]
    
    #write in the database
    path = os.path.normpath(os.path.join(DATADIR, 'User'))
    for i in range(len(str(userName))):
        path = os.path.join(path, userName[i])
        if not os.path.exists(path):
            os.mkdir(path)
    path = os.path.join(path, "UserInformation.data")
    if os.path.exists(path):
        #用户已存在，注册失败
        print("User has existed\n")
        return UserHasExisted
    else:
        #用户不存在
        print("User is not exists\n")
        WriteUserInformation(path, password)
    return 0
        
def Sign_in(data):
    #get information
    data = data.strip()
    dataList = data.split('\t')
    if len(dataList) != 2:
        print("Error: sign_in data has error")
    userName = dataList[0]
    password = dataList[1]
    #print checkUser(userName, password)
    return checkUser(userName, password)

def checkUser(userName, password):
    path = os.path.normpath(os.path.join(DATADIR, 'User'))
    for i in range(len(str(userName))):
        path = os.path.join(path, userName[i])
        if not os.path.exists(path):
            return NotAUser
    path = os.path.join(path, "UserInformation.data")
    if os.path.exists(path):
        #用户存在
        RightPassword = ReadPassword(path)
        if str(password) == str(RightPassword):
            return 0
        else:
            return PasswordError
    else:
        return NotAUser
        
def WriteUserInformation(path, password):
    file = open(path, 'w')
    information = str(password)
    file.write(information)
    file.close()
    
def ReadPassword(path):
    file = open(path, 'r')
    password = file.read()
    return password
    
#Sign_up("mine\t123456")
#Sign_in("mie\t123456")
#Sign_in("mine\t123455")
Sign_in("mine\t123456")