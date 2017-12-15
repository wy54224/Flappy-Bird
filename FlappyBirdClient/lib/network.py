# -*- coding: utf-8 -*-
import socket, netstream
connected = False
sock = None

serialID = 0            #server向客户端发回的序列ID号
isSet = False

def connect(gameScene):
    global connected, sock
    if connected:
        return connected
    #connect server
    host = "127.0.0.1"
    port = 9234
    sock = socket.socket()
    try: 
    	sock.connect((host, port))
    except:
    	connected = False
    	return connected
    
    connected = True

    #始终接收服务端消息
    def receiveServer(dt):
    	global connected, serialID
        if not connected:
            return
        data = netstream.read(sock)
        if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
            return
        
        #客户端SID
        if 'sid' in data:
            serialID = data['sid']

        if 'notice_content' in data:
            import game_controller
            game_controller.showContent(data['notice_content']) #showContent is from game_controller
        
        if 'sign_up_result' in data:
            fix_sign_up_result(data)
        
        if 'sign_in_result' in data:
            print 'get sign in result ', data['sign_in_result']
            fix_sign_in_result(data)
            
        if 're_game_result' in data:
            fix_game_result(data)
            
    gameScene.schedule(receiveServer)
    return connected

def fix_sign_up_result(data):
    import game_controller
    if data['sign_up_result'] == "Failed":
        content = "The userName has been used. Please try again."
        game_controller.showContent(content)
    if data['sign_up_result'] == "Success":
        content = "Register Success!"
        game_controller.showContent(content)
        game_controller.registerSuccessOp()
        
def fix_sign_in_result(data):
    print 'get sign in result ', data['sign_in_result']
    import game_controller
    if data['sign_in_result'] == "notAUser":
        content = "userName is not exist"
        game_controller.showContent(content)
    elif data['sign_in_result'] == "passwordError":
        content = "Password error"
        game_controller.showContent(content)
    elif data['sign_in_result'] == "success":
        game_controller.signInSuccessOp()

def fix_game_result(data):
    #从服务器获取到排名，执行相关操作
    data = data['re_game_result']
    data = data.strip()
    dataList = data.split('\t')
    if len(dataList) != 4:
        print("Error: result data has error")
    bestScore = dataList[0]
    bestTime = dataList[1]
    defeat = dataList[2]
    myRank = dataList[3]
    from pipe import g_score
    import game_controller
    game_controller.setResult(str(g_score), str(bestScore), str(myRank), str(defeat))
    #从服务器收到游戏结果后，显示游戏结果
    import game_controller
    game_controller.backToMainMenu()
    print "receive game rank", data        
 
def get_send_data():
    send_data = {}
    send_data['sid'] = serialID
    return send_data

#向server请求公告
def request_notice():
    send_data = get_send_data()
    send_data['notice'] = 'request notice'
    netstream.send(sock, send_data)
    
#向server发送注册信息
def request_sign_up(account, password):
    data = str(account) + '\t' + str(password)
    send_data = get_send_data()
    send_data['sign_up'] = str(data)
    netstream.send(sock, send_data)
    
#向server发送登陆信息
def request_sign_in(account, password):
    data = str(account) + '\t' + str(password)
    send_data = get_send_data()
    send_data['sign_in'] = data
    netstream.send(sock, send_data)
    print 'have send sign in message'
   
#向server发送游戏结果   
def request_send_result(account, score, survival_time, diificulty):
    data = str(account) + '\t' + str(score) + '\t' + str(survival_time) + '\t' + str(diificulty)
    send_data = get_send_data()
    send_data['game_result'] = data
    netstream.send(sock, send_data)
    