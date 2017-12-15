# -*- coding: utf-8 -*-
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
from cocos.euclid import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import common
from pipe import pipeDistance
import time
import storeInformation

# contactListener
collision_manager = None
collision_func = None

# 判断是否跟新过结果（只第一次才更新结果）
update = False

def addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2):
    global collision_manager, collision_func, upPipeCollided, isCollided, update
    #初始化为未跟新结果
    update = False
    #设置land区域对应的刚体
    landSprite = CollidableRectSprite("land", (common.visibleSize["width"])/2, (atlas["land"]["height"] / 4 - 3), (common.visibleSize["width"])/2, (atlas["land"]["height"])/2)

    #pipe对应的刚体在pipe.py中设置
    pipes = getPipes()
    pipeCount = getPipeCount()
    upPipeY = getUpPipeYPosition()
    upPipeCollided = False
    isCollided = False

    #初始化碰撞管理器
    collision_manager = CollisionManagerBruteForce()
    #添加刚体到管理器中，从而处理刚体之间的碰撞关系
    collision_manager.add(landSprite)
    collision_manager.add(spriteBird)
    for i in range(0, pipeCount):
        collision_manager.add(pipes[i].get("downPipe"))
        collision_manager.add(pipes[i].get("upPipe"))

    def collisionHandler(dt):
        global isCollided, upPipeCollided, collision_func
        spriteBird.cshape.center = Vector2(spriteBird.position[0], spriteBird.position[1])
        for i in range(0, pipeCount):
            pipes[i].get("downPipe").cshape.center = Vector2(pipes[i].position[0], pipes[i].position[1]+(atlas["pipe_up"]["height"] + pipeDistance[i]))
            pipes[i].get("upPipe").cshape.center = Vector2(pipes[i].position[0], pipes[i].position[1])

        for other in collision_manager.iter_colliding(spriteBird):
            if other.name == 'land':
                print "on Contact Between Bird And Land Begin"
                spriteBird.gravity = 0
                upPipeCollided = True
            else:
                print "on Contact Between Bird And Pipe Begin"
                birdXPosition = spriteBird.position[0]
                birdYPosition = spriteBird.position[1]
                for i in range(0, pipeCount):
                    if (pipes[i].position[0]-atlas["pipe_up"]["width"]/2) <= birdXPosition and (pipes[i].position[0]+atlas["pipe_up"]["width"]/2) >= birdXPosition:
                        if (birdYPosition - upPipeY[i]) <= 25:
                            upPipeCollided = True
                            spriteBird.gravity = 0
                            break
                        else:
                            upPipeCollided = False
                            break
            isCollided = True

        if isCollided:
            gameOver(gameScene, land_1, land_2, spriteBird, upPipeCollided)

    collision_func = collisionHandler
    gameScene.schedule(collisionHandler)

def gameOver(gameScene, land_1, land_2, spriteBird, upPipeCollided):
	#游戏结束，记录本局结果
    global update
    if not update:
        updateGameResult()
        update = True
	
    global collision_func
    land_1.stop()
    land_2.stop()

    removeMovePipeFunc(gameScene)
    removeCalScoreFunc(gameScene)
    removeBirdTouchHandler(gameScene)
    if upPipeCollided and collision_func:
        gameScene.unschedule(collision_func)
        spriteBird.stop()
        import game_controller
        game_controller.backToMainMenu()

def updateGameResult():
    from pipe import g_score
    from game_controller import account
    from game_controller import TimeStart
    from game_controller import difficulty
    from network import request_send_result
    Time_End = time.clock()
    elapsed = Time_End - TimeStart
    WriteResult_tmp(g_score, elapsed)
    WriteResult_HistoryResult(account, g_score, elapsed, difficulty)
    request_send_result(account, g_score, elapsed, difficulty)