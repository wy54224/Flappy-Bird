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
import common
import random

#vars
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False
#难度选择 0是简单 1是普通 2是困难
difficulty = 0

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
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=50)

def showNotice():
    connected = connect(gameScene) # connect is from network.py
    if not connected:
        content = "Cannot connect to server"
        showContent(content)
    else:
        request_notice() # request_notice is from network.py

def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")

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
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice))
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        singleGameReady()

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
        difficulty_button = SingleDifficultyChooseMenu()
        gameLayer.add(difficulty_button, z=90, name="difficulty_button")

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
        singleGameReady()

    def setMiddle(self):
        gameLayer.remove("difficulty_button")
        global difficulty
        difficulty = 1
        singleGameReady()

    def setHard(self):
        gameLayer.remove("difficulty_button")
        global difficulty
        difficulty = 2
        singleGameReady()

class SingleLoginMenu(Menu):
    def __init__(self):
        super(SingleLoginMenu, self).__init__()
        usertext = EntryMenuItem('U:', self.gameUsername, "", 12)
        passtext = EntryMenuItem('P:', self.gamePassword, "", 12)
        loginbutton = ImageMenuItem(common.load_image("button_login.png"), self.gameLogin)
        registerbutton = ImageMenuItem(common.load_image("button_register.png"), self.gameRegister)
        self.font_item['font_size'] = 15
        self.font_item_selected['font_size'] = 25
        items = [
                usertext,
                passtext,
                loginbutton,
                registerbutton
                ]
        self.create_menu(items, selected_effect=shake(),unselected_effect=shake_back())
        self.font_item['font_size'] = 38
        self.font_item_selected['font_size'] = 48

    def gameLogin(self):
        LeaveLoginContext()
        start_button = SingleGameStartMenu()
        gameLayer.add(start_button, z=90, name="start_button")

    def gameRegister(self):
        gameLayer.remove("login_button")

    def gameUsername(self, value):
        pass

    def gamePassword(self, value):
        pass

def AddLoginContext():
    #login_botton = SingleLoginMenu()
    #gameLayer.add(login_botton, z=20, name="login_button")
    start_button = SingleGameStartMenu()
    gameLayer.add(start_button, z=90, name="start_button")

def LeaveLoginContext():
    gameLayer.remove("login_button")
