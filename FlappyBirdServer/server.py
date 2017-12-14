# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback
import databaseOp

HOST = "127.0.0.1"
disconnected_list = []#断开连接的客户端列表
onlineUser = {}
sid = 0

#处理注册消息
def fix_sign_up(recvData):
    number = recvData['sid']
    print 'receive sign_up request from user id:', number
    result = databaseOp.Sign_up(recvData['sign_up'])
    if result == databaseOp.UserHasExisted:
        #如果用户已经存在
        number = recvData['sid']
        sendData = {"sign_up_result": "Failed"}
        netstream.send(onlineUser[number]['connection'], sendData)
    elif result == 0:
        number = recvData['sid']
        sendData = {"sign_up_result": "Success"}
        netstream.send(onlineUser[number]['connection'], sendData)
 
#处理登陆消息 
def fix_sign_in(recvData):
    number = recvData['sid']
    print 'receive sign_up request from user id:', number
    result = databaseOp.Sign_in(recvData['sign_in'])
    if result == databaseOp.NotAUser:
        #用户不存在
        number = recvData['sid']
        sendData = {"sign_in_result": "notAUser"}
        netstream.send(onlineUser[number]['connection'], sendData)
    elif result == databaseOp.PasswordError:
        number = recvData['sid']
        sendData = {"sign_in_result": "passwordError"}
        netstream.send(onlineUser[number]['connection'], sendData)
    elif result == 0:
        number = recvData['sid']
        sendData = {"sign_in_result": "success"}
        netstream.send(onlineUser[number]['connection'], sendData)

#处理收到游戏结果的消息
def fix_game_result(recvData):
    number = recvData['sid']
    print 'receive sign_up request from user id:', number
    bestScore, bestTime, totalPerson, myRank = databaseOp.store_Result(recvData['game_result'])
    number = recvData['sid']
    #给客户端发送排名信息
    information = str(bestScore) + '\t' + str(bestTime) + '\t' + str(totalPerson) + '\t' + str(myRank)
    sendData = {"re_game_result": information}
    netstream.send(onlineUser[number]['connection'], sendData)
       
if __name__ == "__main__":
	s = socket.socket()

	host = HOST
	port = 9234

	s.bind((host, port))
	s.listen(5)

	inputs = []
	inputs.append(s)
	print 'server start! listening host:', host, ' port:', port

while inputs:
    try:
        rs, ws, es = select.select(inputs, [], [])
        for r in rs:
            if r is s:
                print 'sid:', sid
				# accept
                connection, addr = s.accept()
                print 'Got connection from' + str(addr)
                inputs.append(connection)
                sendData = {}
                sendData['sid'] = sid
                netstream.send(connection, sendData)

                cInfo = {}
                cInfo['connection'] = connection
                cInfo['addr'] = str(addr)
                cInfo['ready'] = False
                onlineUser[sid] = cInfo
                print(str(onlineUser))
                sid += 1
            else:
				# receive data
                recvData = netstream.read(r)
				# print 'Read data from ' + str(r.getpeername()) + '\tdata is: ' + str(recvData)
				# socket关闭
                if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT:
                    if r.getpeername() not in disconnected_list:
                        print str(r.getpeername()) + 'disconnected'
                        disconnected_list.append(r.getpeername())
                else:  # 根据收到的request发送response
					#公告
                    if 'notice'in recvData:
                        number = recvData['sid']
                        print 'receive notice request from user id:', number
                        sendData = {"notice_content": "This is a notice from server. Good luck!"}
                        netstream.send(onlineUser[number]['connection'], sendData)
                    elif 'sign_up'in recvData:
                        fix_sign_up(recvData)
                    elif 'sign_in' in recvData:
                        fix_sign_in(recvData)
                    elif 'game_result' in recvData:
                        fix_game_result(recvData)
    except Exception:
        traceback.print_exc()
        print 'Error: socket 链接异常'
        