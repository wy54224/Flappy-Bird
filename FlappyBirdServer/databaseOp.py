# -*- coding: utf-8 -*-
import os
import re

#用于注册
UserHasExisted = -1
#用于登陆
NotAUser = -2
PasswordError = -3
#写入信息
FAILED = -4
SUCCESS = 0
#存储每个用户最好的成绩的个数
MAX_ITEM = 3

DATADIR = os.path.normpath(os.path.join('.', 'DataBase'))

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

def store_Result(data):
    data = data.strip()
    dataList = data.split('\t')
    if len(dataList) != 4:
        print("Error: result data has error")
    userName = dataList[0]
    score = dataList[1]
    survivalTime = dataList[2]
    difficulty = dataList[3]
    bestScore, bestTime = store_result_in_UserBest(userName, score, survivalTime, difficulty)
    totalPerson, myRank = store_result_in_rank(userName, score, survivalTime, difficulty)
    return bestScore, bestTime, totalPerson, myRank
    
#判断登陆信息是否正确
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
        
#写入password信息
def WriteUserInformation(path, password):
    file = open(path, 'w')
    information = str(password)
    file.write(information)
    file.close()
    
#读入password信息
def ReadPassword(path):
    file = open(path, 'r')
    password = file.read()
    return password
    
#将结果存入用户表(存储最好MAX_ITEM次成绩)
def store_result_in_UserBest(userName, score, survivalTime, difficulty):
    path = os.path.normpath(os.path.join(DATADIR, 'User'))
    for i in range(len(str(userName))):
        path = os.path.join(path, userName[i])
    path = os.path.join(path, str(difficulty)+'.data')
    information = str(score) + '\t' + str(survivalTime)
    if not os.path.exists(path):
        file = open(path, 'w')
        file.close()
    file = open(path, 'r')
    DataMat = getRank(file, score, survivalTime)
    file.close()
    file = open(path, 'w')
    for i in range(len(DataMat)):
        data = str(DataMat[i][0]) + '\t' + str(DataMat[i][1]) + '\t' + str(DataMat[i][2]) + '\n'
        file.write(data)
    file.close()
    return DataMat[0][1], DataMat[0][2]
        
def store_result_in_rank(userName, score, survivalTime, difficulty):
    path = createDir(DATADIR, 'Rank')
    path = createDir(path, str(difficulty))
    totalRankPath = os.path.normpath(os.path.join(path, 'TotalRank.data'))
    
    TotalPerson, myRank = changeTotalRank(totalRankPath, score)  #更新主索引文件,并获得排名
    
    path = createDir(path, str(score))          #进入了分数的子文件夹
    path = os.path.normpath(os.path.join(path, 'Rank.data'))
    changeRank(path, userName, survivalTime)
    return TotalPerson, myRank
    
#判断游戏结果在自己最高成绩中排在第几位,并将其插入数据中
def getRank(File, Score, Time):
	arrayOfLines = File.readlines()
	numOfLines = len(arrayOfLines)
	DataMat = []
	#解析文件数据到DataMat
	index = 0
	isInsert = False
	for line in arrayOfLines:
		line = line.strip()
		listFromLine = line.split('\t')
		if len(listFromLine) == 3:
			DataMat.append(listFromLine[0:3])
			if not isInsert and cmp(Score, DataMat[index][1], Time, DataMat[index][2]):
				#找到了插入的位置
				temp = DataMat[index]
				DataMat[index] = [0, Score, Time]
				DataMat.append(temp)
				index += 1
				isInsert = True
			index += 1
			if index >= MAX_ITEM:
				break;
		else:
			print("Error: Read Data File Error\n")
			break;	
	
	#如果文件没有被插入进数据中，并且数据还有空位
	if len(DataMat) < MAX_ITEM and not isInsert:
		DataMat.append([0, Score, Time])
	# update number
	for i in range(len(DataMat)):
		DataMat[i][0] = i + 1
	return DataMat

#更新总排名表的主索引文件,同时可以获取到该用户的排名
def changeTotalRank(path, score):
    TotalPerson = 1
    myRank = 1
    if not os.path.exists(path):
        rankFile = open(path, 'w')
        rankFile.close()
    #读出数据
    DataMat = readData(path, 2)
    
    #修改数据
    insert = False
    length = len(DataMat)
    for i in range(length):
        TotalPerson += int(DataMat[i][1])
        if int(score) == int(DataMat[i][0]) and not insert:
            DataMat[i][1] = str(int(DataMat[i][1]) + int(1))
            insert = True
        elif int(score) > int(DataMat[i][0]) and int(score) != int(DataMat[i-1][0]) and not insert:
            DataMat.insert(i, [str(score), str(1)])
            insert = True
        if not insert:
            myRank += int(DataMat[i][1])
    if not insert:
        DataMat.append([str(score), str(1)])
    #写回数据
    writeData(path, 2, DataMat)
    return TotalPerson, myRank
        
#更新某分数下的rank文件
def changeRank(path, userName, Time):
    if not os.path.exists(path):
        rankFile = open(path, 'w')
        rankFile.close()
    rankFile = open(path, 'a')
    information = str(userName) + '\t' + str(Time) + '\n'
    rankFile.write(information)
    rankFile.close()


#比较算子        
def cmp(Score1, Score2, Time1, Time2):
	if int(Score1) > int(Score2):
		return True
	elif int(Score1) == int(Score2):
		return Time1 > Time2
	else:
		return False    
        
def createDir(path, child):
    path = os.path.normpath(os.path.join(path, child))
    if not os.path.exists(path):
        os.mkdir(path)
    return path
    
def readData(path, numOfLines):
    totalRankFile = open(path, 'r')
    DataMat = []
    arrayOfLines = totalRankFile.readlines()
    for line in arrayOfLines:
        line = line.strip()
        listFromLine = line.split('\t')
        if len(listFromLine) == numOfLines:
            DataMat.append(listFromLine[0:numOfLines])
    totalRankFile.close()
    return DataMat
    
def writeData(path, numOfLines, DataMat):
    totalRankFile= open(path, 'w')
    for i in range(len(DataMat)):
        data = ""
        for j in range(numOfLines):
            data += (str(DataMat[i][j]) + '\t')
        data += '\n'
        totalRankFile.write(data)
    totalRankFile.close()
