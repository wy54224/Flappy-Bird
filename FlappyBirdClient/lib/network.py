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
            fix_sign_in_result(data)
            
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
    import game_controller
    if data['sign_in_result'] == "notAUser":
        content = "userName is not exist"
        game_controller.showContent(content)
    elif data['sign_in_result'] == "passwordError":
        content = "Password error"
        game_controller.showContent(content)
    elif data['sign_in_result'] == "success":
        game_controller.signInSuccessOp()

 
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
    
def request_send_result(account, score, survival_time, diificulty):
    data = str(account) + '\t' + str(score) + '\t' + str(survival_time) + '\t' + str(diificulty)
    send_data = get_send_data()
    send_data['game_result'] = data
    netstream.send(sock, send_data)