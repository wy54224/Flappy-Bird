# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from network import *
from regular_expression import *
import common
import random
import time
import storeInformation
from six import string_types
from pyglet.window import key
from pyglet import font

#vars
TimeStart =  None
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
ipTextField = None
errorLabel = None
isGamseStart = False
#难度选择 0是简单 1是普通 2是困难
difficulty = 0
#当前所处页面使用的menu（若无为None)
currentMenu = None
current = None
#账号信息
account = None
password = None
passwordRepeat = None

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    # add moving bird
    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
    gameScene.add(gameLayer)

def game_start(_gameScene):
    global gameScene
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    #start_botton = SingleGameStartMenu()
    #gameLayer.add(start_botton, z=20, name="start_button")
    menu_button = SingleMainMenu()
    gameLayer.add(menu_button, z=20, name="menu_button")
    AddLoginContext()
    connect(gameScene)

def createLabel(value, x, y):
    label=Label(value,
        font_name='Times New Roman',
        font_size=15,
        color = (0,0,0,255),
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label

# single game start button的回调函数
def singleGameReady():
    removeContent()
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)

    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)

        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            isGamseStart = True
            global TimeStart
            TimeStart = time.clock()
			
            spriteBird.gravity = gravity #gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            global difficulty
            if(difficulty == 0):
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, 120)
            elif(difficulty == 1):
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, 80)
            else:
                pipes = createPipes(gameLayer, gameScene, spriteBird, score, 60)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

def backToMainMenu():
    global current
    current = RestartMenu()
    global currentMenu
    currentMenu = "restart_button"
    gameLayer.add(current, z=50, name="restart_button")

def showNotice():
    connected = connect(gameScene) # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        request_notice() # request_notice is from network.py

def showContent(content):
    removeContent()
    content = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(content, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass


class RestartMenu(Menu):
    def __init__(self):
        super(RestartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_difficulty.png"), self.initDifficultyMenu)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        menu_button = SingleMainMenu()
        gameLayer.add(menu_button, z=20, name="menu_button")
        global current
        global currentMenu
        current = None
        currentMenu = None
        singleGameReady()

    def initDifficultyMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        menu_button = SingleMainMenu()
        gameLayer.add(menu_button, z=20, name="menu_button")
        global current
        current = SingleDifficultyChooseMenu()
        global currentMenu
        currentMenu = "difficulty_button"
        gameLayer.add(current, z=90, name="difficulty_button")

class SingleGameStartMenu(Menu):
    def __init__(self):
        super(SingleGameStartMenu, self).__init__()
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStart(self):
        gameLayer.remove("start_button")
        global current
        current = SingleDifficultyChooseMenu()
        global currentMenu
        currentMenu = "difficulty_button"
        gameLayer.add(current, z=90, name="difficulty_button")

class SingleDifficultyChooseMenu(Menu):
    def __init__(self):
        super(SingleDifficultyChooseMenu, self).__init__()
        items = [
                (ImageMenuItem(common.load_image("button_easy.png"), self.setEasy)),
                (ImageMenuItem(common.load_image("button_middle.png"), self.setMiddle)),
                (ImageMenuItem(common.load_image("button_hard.png"), self.setHard))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def setEasy(self):
        gameLayer.remove("difficulty_button")
        global difficulty
        difficulty = 0
        global current
        current = None
        global currentMenu
        currentMenu = None
        singleGameReady()

    def setMiddle(self):
        gameLayer.remove("difficulty_button")
        global difficulty
        difficulty = 1
        global current
        current = None
        global currentMenu
        currentMenu = None
        singleGameReady()

    def setHard(self):
        gameLayer.remove("difficulty_button")
        global difficulty
        difficulty = 2
        global current
        current = None
        global currentMenu
        currentMenu = None
        singleGameReady()

'''Menu菜单'''
class SingleMenu(Menu):
        def __init__(self):
            super(SingleMenu, self).__init__()
            items = [
                    (ImageMenuItem(common.load_image("button_logout.png"), self.logOut)),
                    (ImageMenuItem(common.load_image("button_notice.png"), self.logOut))
                    ]
            self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

        def logOut(self):
            gameScene.remove("MainMenu")
            gameOver(gameScene, land_1, land_2, spriteBird, True)
            if(currentMenu == "restart_button" and current):
                gameLayer.remove(currentMenu)
            gameScene.remove(gameLayer)
            initGameLayer()
            isGamseStart = False
            menu_button = SingleMainMenu()
            gameLayer.add(menu_button, z=20, name="menu_button")
            AddLoginContext()

'''Menu按钮'''
class SingleMainMenu(Menu):
    isShow = False
    def __init__(self):
        super(SingleMainMenu, self).__init__()
        Menu = ImageMenuItem(common.load_image("button_menu.png"), self.showMain)
        items = [Menu]
        self.create_menu(items)
        width, height = director.get_window_size()
        pos_x = width // 2
        pos_y = height - Menu.get_item_height() // 2
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 19
        Menu.generateWidgets(pos_x, pos_y, self.font_item, self.font_item_selected)

    def showMain(self):
        self.isShow = not self.isShow
        global current
        global currentMenu
        global isPause
        if(self.isShow):
            spriteBird.pause()
            gameScene.pause_scheduler()
            singlemenu = SingleMenu()
            gameScene.add(singlemenu, name="MainMenu")
            if(currentMenu and current):
                gameLayer.remove(currentMenu)
        else:
            gameScene.remove("MainMenu")
            spriteBird.resume()
            gameScene.resume_scheduler()
            if(currentMenu and current):
                gameLayer.add(current, z=70, name = currentMenu)

'''自定义的文本输入框'''
class MyOwnEntryItem(MenuItem):
    value = property(lambda self: u''.join(self._value),
                     lambda self, v: setattr(self, '_value', list(v)))
    show = True
    background = None

    def __init__(self, label, show, callback_func, value, max_length=0):
        self._value = list(value)
        self._label = label
        self.show = show
        super(MyOwnEntryItem, self).__init__("%s %s" % (label, value), callback_func)
        self.max_length = max_length
        self.background = CollidableRectSprite("text", -15, -15, pipeWidth/2, pipeHeight/2)
        self.add(self.background, z = -1);

    def on_text(self, text):
        if self.max_length == 0 or len(self._value) < self.max_length:
            self._value.append(text)
            self._calculate_value()
        return True

    def on_key_press(self, symbol, modifiers):
        if symbol == key.BACKSPACE:
            try:
                self._value.pop()
            except IndexError:
                pass
            self._calculate_value()
            return True

    def _calculate_value(self):
        self.callback_func(self.value)
        if(self.show):
            new_text = u"%s %s" % (self._label, self.value)
        else:
            s = ""
            for c in self.value:
                s += "*"
            new_text = u"%s %s" % (self._label, s)
        self.item.text = new_text
        self.item_selected.text = new_text

    def OwnGenerateWidgets(self, pos_x, pos_y, font_item, font_item_selected):
        self.generateWidgets(pos_x, pos_y, font_item, font_item_selected)
        self.background.position = (pos_x, pos_y)
        width, height = director.get_window_size()
        self.background.scale_x = width * 0.7 / self.background.width
        self.background.scale_y = self.get_item_height() * 1.0 / self.background.height

class SingleLoginMenu(Menu):
    def __init__(self):
        super(SingleLoginMenu, self).__init__()
        userlabel = MenuItem('Username:', None)
        usertext = MyOwnEntryItem('', True, self.gameUsername, "", 12)
        passlabel = MenuItem('Password:', None)
        passtext = MyOwnEntryItem('', False, self.gamePassword, "", 12)
        loginbutton = ImageMenuItem(common.load_image("button_login.png"), self.gameLogin)
        registerbutton = ImageMenuItem(common.load_image("button_register.png"), self.gameRegister)
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 17
        items = [
                userlabel,
                usertext,
                passlabel,
                passtext,
                loginbutton,
                registerbutton
                ]
        self.create_menu(items)
        width, height = director.get_window_size()
        pos_x = width // 2
        pos_y = height // 2
        self.font_item['font_size'] = 38
        self.font_item_selected['font_size'] = 39
        loginbutton.generateWidgets(pos_x - 40, pos_y - 20, self.font_item, self.font_item_selected)
        registerbutton.generateWidgets(pos_x + 40, pos_y - 20, self.font_item, self.font_item_selected)
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 17
        self.font_item_selected['color'] = (0, 0, 0, 255)
        self.font_item['color'] = (0, 0, 0, 255)
        usertext.OwnGenerateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 2 + 25, self.font_item, self.font_item_selected)
        passtext.OwnGenerateWidgets(pos_x, pos_y + 25, self.font_item, self.font_item_selected)
        self.font_item_selected['font_size'] = 15
        userlabel.generateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 3 + 25, self.font_item, self.font_item_selected)
        passlabel.generateWidgets(pos_x, pos_y + self.font_item['font_size'] + 8 + 25, self.font_item, self.font_item_selected)

    def gameLogin(self):
        '''在这里添加帐号密码判断的逻辑'''
        import regular_expression
        if regular_expression.userNameMatchFinal(account) and regular_expression.passwordMatchFinal(password):
            connected = connect(gameScene) # connect is from network.py
            if not connected:
                content = "Cannot connect to server"
                showContent(content)
            else:
                request_sign_in(account, password) # request_notice is from network.py
        else:
            content = 'password or account has wrong format, please try again'
            showContent(content)

    def gameRegister(self):
        LeaveLoginContext()
        global current
        current = SingleRegisterMenu()
        global currentMenu
        currentMenu = "register_button"
        gameLayer.add(current, z=90, name="register_button")

    def gameUsername(self, value):
        '''这里的value是输入的帐号'''
        removeContent()
        global account
        account = value
        print value
        pass

    def gamePassword(self, value):
        '''这里的value是输入的密码'''
        removeContent()
        global password
        password = value
        print value
        pass

class SingleRegisterMenu(Menu):
    def __init__(self):
        super(SingleRegisterMenu, self).__init__()
        #初始化账号信息为空
        initializeRegisterInformation()
        
        userlabel = MenuItem('Username:', None)
        usertext = MyOwnEntryItem('', True, self.gameUsername, "", 12)
        passlabel = MenuItem('Password:', None)
        passtext = MyOwnEntryItem('', False, self.gamePassword, "", 12)
        passagainlabel = MenuItem('Password Again:', None)
        passagaintext = MyOwnEntryItem('', False, self.gamePasswordAgain, "", 12)
        registerbutton = ImageMenuItem(common.load_image("button_register.png"), self.gameRegister)
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 17
        items = [
                userlabel,
                usertext,
                passlabel,
                passtext,
                passagainlabel,
                passagaintext,
                registerbutton
                ]
        self.create_menu(items)
        width, height = director.get_window_size()
        pos_x = width // 2
        pos_y = height // 2
        self.font_item['font_size'] = 38
        self.font_item_selected['font_size'] = 39
        registerbutton.generateWidgets(pos_x, pos_y - 20, self.font_item, self.font_item_selected)
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 17
        self.font_item_selected['color'] = (0, 0, 0, 255)
        self.font_item['color'] = (0, 0, 0, 255)
        usertext.OwnGenerateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 4 + 25, self.font_item, self.font_item_selected)
        passtext.OwnGenerateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 2 + 25, self.font_item, self.font_item_selected)
        passagaintext.OwnGenerateWidgets(pos_x, pos_y + 25, self.font_item, self.font_item_selected)
        self.font_item_selected['font_size'] = 15
        userlabel.generateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 5 + 25, self.font_item, self.font_item_selected)
        passlabel.generateWidgets(pos_x, pos_y + (self.font_item['font_size'] + 8) * 3 + 25, self.font_item, self.font_item_selected)
        passagainlabel.generateWidgets(pos_x, pos_y + self.font_item['font_size'] + 8 + 25, self.font_item, self.font_item_selected)

    def gameRegister(self):
        '''在这里添加注册的判断逻辑'''
        import regular_expression
        if regular_expression.userNameMatchFinal(account) and regular_expression.passwordMatchFinal(password):
            connected = connect(gameScene) # connect is from network.py
            if not connected:
                content = "Cannot connect to server"
                showContent(content)
            else:
                request_sign_up(account, password) # request_notice is from network.py

    def gameUsername(self, value):
        removeContent()
        '''这里的value是输入的帐号'''
        global account
        account = value
        #---进行用户名格式判断---#
        import regular_expression
        result = regular_expression.userNameMatch(account)
        print result
        if result == regular_expression.FIRSTPOS_ERROR:
            content = 'the first location of username must be a letter'
            showContent(content)
        elif result == regular_expression.CHARACTER_ERROR:
            content = 'username can only contain letter, number, underline'
            showContent(content)
        elif result == regular_expression.LENGTH_ERROR:
            content = 'the length of username should be less than 16 characters'
            showContent(content)
        #------------------------#
        print value

    def gamePassword(self, value):
        removeContent()
        '''这里的value是输入的密码'''
        global password
        password = value
        #---进行密码格式判断---#
        import regular_expression
        result = regular_expression.passwordPatternMatch(password)
        if result == regular_expression.CHARACTER_ERROR:
            content = 'password can not contain space, tab and so on'
            showContent(content)
        elif result == regular_expression.LENGTH_ERROR:
            content = 'the lenth of password should be between 6 and 16 characters'
            showContent(content)
        #------------------------#
        print value

    def gamePasswordAgain(self, value):
        removeContent()
        '''这里的value是输入的确认密码'''
        global passwordRepeat
        passwordRepeat = value
        #---判断两次密码是否相等---#
        import regular_expression
        if not regular_expression.passwordSame(password, passwordRepeat):
            content = 'the two password is not same, please check them again'
            showContent(content)
        #--------------------------#
        print value

def AddLoginContext():
    global current
    current = SingleLoginMenu()
    global currentMenu
    currentMenu = "login_button"
    gameLayer.add(current, z=20, name="login_button")
    # start_button = SingleGameStartMenu()
    # gameLayer.add(start_button, z=90, name="start_button")

def LeaveLoginContext():
    gameLayer.remove("login_button")

#register success, update UI
def registerSuccessOp():
    '''下面是注册成功时的操作'''
    print("register success\n")
    removeContent()
    gameLayer.remove("register_button")
    AddLoginContext()

#sign in success, updata UI
def signInSuccessOp():
    '''下面是当帐号密码通过时的操作'''
    LeaveLoginContext()
    global current
    current = SingleGameStartMenu()
    global currentMenu
    currentMenu = "start_button"
    gameLayer.add(current, z=90, name="start_button")    
   
def initializeRegisterInformation():
    global account, password, passwordRepeat
    account = None
    password = None
    passwordRepeat = None
    