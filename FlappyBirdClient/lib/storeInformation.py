# -*- coding: utf-8 -*-
import os
import re
from common import TEMPDIR

#common#
MAX_ITEM = 5   #客户端只存每个用户最优的5次成绩

def WriteInformation_tmp(Score, Time):
	File_Information = open(os.path.join(TEMPDIR, 'tmp_Information.tmp'), 'a')
	Information = str(Score) + "  " + str(Time) + "\n"
	print(Information)
	File_Information.write(Information)
	File_Information.close()
	
def WriteResult_tmp(Score, Time):
	File_Information = open(os.path.join(TEMPDIR, 'tmp_Information.tmp'), 'a')
	File_Information.write("---Game Result---\n")
	File_Information.write("Score: " + str(Score) + "\n")
	File_Information.write("Survival Time: " + str(Time) + "\n\n")
	File_Information.close()
	
def Clear_tmp():
    File_Information = os.path.join(TEMPDIR, 'tmp_Information.tmp')
    if os.path.exists(File_Information):
        os.remove(File_Information)
	
# ######################
# 存储格式
# Rank Score SurvivalTime
# ######################
def WriteResult_HistoryResult(ID, Score, Time, difficulty):
	File_History_Dir = os.path.join(TEMPDIR, 'HistoryResult')
	if not os.path.exists(File_History_Dir):
		os.mkdir(File_History_Dir)
	File_History_Dir = os.path.join(File_History_Dir, str(ID))
	if not os.path.exists(File_History_Dir):
		os.mkdir(File_History_Dir)
	File_History_Dir = os.path.join(File_History_Dir, str(difficulty) + '.data')
	if not os.path.exists(File_History_Dir):
		fl = open(File_History_Dir, 'w')
		fl.close()
	
	File_History = open(File_History_Dir, 'r')
	DataMat = getRank(File_History, Score, Time)
	print(DataMat)
	print("\n")
	File_History.close()
	File_History = open(File_History_Dir, 'w')
	for i in range(len(DataMat)):
		data = str(DataMat[i][0]) + '\t' + str(DataMat[i][1]) + '\t' + str(DataMat[i][2]) + '\n'
		File_History.write(data)
	File_History.close()
		
	
#判断游戏结果排在第几位,并将其插入数据中
def getRank(File, Score, Time):
	arrayOfLines = File.readlines()
	numOfLines = len(arrayOfLines)
	DataMat = []
	#解析文件数据到DataMat
	index = 0
	isInsert = False
	#如果文件为空
	for line in arrayOfLines:
		line = line.strip() #注释1
		listFromLine = line.split('\t') #注释2
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
			
def cmp(Score1, Score2, Time1, Time2):
	if int(Score1) > int(Score2):
		return True
	elif int(Score1) == int(Score2):
		return Time1 > Time2
	else:
		return False