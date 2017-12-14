# -*- coding: utf-8 -*-
import re

#error#
FIRSTPOS_ERROR = -1
CHARACTER_ERROR = -2
LENGTH_ERROR = -3
#######

passwordLegal = re.compile('^(\S)+$')
passwordLength = re.compile('^(\S){6,16}$')
userNameFirstPos = re.compile('^[A-Za-z]')
userNameLegal = re.compile('^[A-Za-z]([A-Za-z0-9]|_)*$')
userNameLength = re.compile('^[A-Za-z]([A-Za-z0-9]|_){0,14}$')

def userNameMatch(userName):
    result = userNameFirstPos.match(str(userName))
    if result == None:
        return FIRSTPOS_ERROR
    else:
        result = userNameLegal.match(str(userName))
        if result == None:
            return CHARACTER_ERROR
        else:
            result = userNameLength.match(str(userName))
            if result == None:
                return LENGTH_ERROR
            else:
                return 0

def passwordPatternMatch(password):
    result = passwordLegal.match(str(password))
    if result == None:
        return CHARACTER_ERROR
    else:
        result = passwordLength.match(str(password))
        if result == None:
            return LENGTH_ERROR
        else:
            return 0

def passwordSame(pw1, pw2):
    return pw1 == pw2
    
def userNameMatchFinal(userName):
    result = userNameLength.match(str(userName))
    return result != None
    
def passwordMatchFinal(password):
    result = passwordLength.match(str(password))
    return result != None
