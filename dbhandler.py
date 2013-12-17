# -*- coding: utf-8 -*-
import pymongo
import conf
import threading

def writeInfo(info):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]

    infoCol = db.Info
    mainInfo = {
        "name":info["name"],
        "userID":info["id"],
        "domain":info["domain"],
        "followNum":info["followNum"],
        "fansNum":info["fansNum"],
        "weiboNum":info["weiboNum"],
        "level":info["level"]
    }
    infoCol.insert(mainInfo)
    return True


#Read a userID to crawl 
def readCandidateID():
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    CandidateIDCol = db.CandidateID
    candidate = CandidateIDCol.find(limit=1,field="userID")
    if candidate.count() == 0:
        return None
    return candidate.__getitem__(0).get("userID")

#Remove the user whose info has been crawled
def removeCandidateID(id):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    CandidateIDCol = db.CandidateID
    ProcessedIDCol = db.ProcessedID
    CandidateIDCol.remove({"userID":id})
    ProcessedIDCol.insert({"userID":id})
    return True

#Test whether the specifc user has been processed
def hasBeenProcess(id):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    ProcessedIDCol = db.ProcessedID
    if ProcessedIDCol.find({"userID":id}).count() == 0:
        return False
    else:
        return True

def createIndex():
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    CandidateIDCol = db.CandidateID
    ProcessedIDCol = db.ProcessedID
    CandidateIDCol.create_index([("userID",pymongo.ASCENDING)])
    ProcessedIDCol.create_index([("userID",pymongo.ASCENDING)])

fansLock = threading.Lock() #To keep consistency
def writeFans(list, userID):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    CandidateIDCol = db.CandidateID
    FansCol = db.Fans
    for id in list:
        fansLock.acquire()
        if CandidateIDCol.find({"userID":id}).count() == 0: #Avoid repetition
            CandidateIDCol.insert({"userID":id})
        fansLock.release()
        FansCol.insert({"userID":userID, "fanID":id})
    return True

followLock = threading.Lock() #To keep consistency
def writeFollows(list, userID):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    CandidateIDCol = db.CandidateID
    FollowsCol = db.Follows
    for id in list:
        followLock.acquire()
        if CandidateIDCol.find({"userID":id}).count() == 0: #Avoid repetition
            CandidateIDCol.insert({"userID":id})
        followLock.release()
        FollowsCol.insert({"userID":userID, "followID":id})
    return True

def writeWeibo(list, userID):
    connection = pymongo.Connection('localhost', 27017)
    db = connection[conf.database]
    weiboCol = db.weibo
    for info in list:
        weiboCol.insert(
            {
            "userID":userID, 
            "wbText":info['wbText'], 
            "repostText":info["repostText"],
            "time":info["time"],
            "zanNum":info["zanNum"],
            "commentNum":info["commentNum"],
            "repostNum":info["repostNum"]
            })
    return True