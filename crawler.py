#!/usr/bin/python
# -*- coding: utf-8 -*- 
import urllib2
import re
import chardet
import sys
import login
import parser
import dbhandler
import exception
import conf
import time
import logging
import threading
import thread
import errno
import socket

def getInfo(url, cookie,logPath):
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}
    count = 1
    timesToWait = 1 #the times of conf.waitTime to wait
    while(count > 0):
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read() 
            if parser.errorPage(page) == True:
                logging.warning("Get error page " + url)
                print "Get error page " + url
                return "error"
            newUrl = parser.resetUrl(page)
            if newUrl != None:
                url = newUrl
                req = urllib2.Request(url, headers=HEADERS)
                page  = urllib2.urlopen(req).read() 
        except socket.error as e:
            if count < 1:
                return None
            logging.warning(e)
            print e
            if e.errno == errno.ECONNREFUSED: #when sina.com has detected the crawling, wait for enough time to reconnect
                timesToWait = timesToWait * 2;
                logging.info("Sleep:\t" + str(timesToWait * conf.waitTime)) #'timesToWait' times of the conf.waitTime
                print "Sleep:\t" + str(timesToWait * conf.waitTime)
                time.sleep(timesToWait * conf.waitTime)
                count = count - 1
                continue
        except Exception, e:
            logging.warning(e)
            print e
            return None
        count = count - 1

    try:
        info = parser.parseInfo(page)
    except exception.ParseInfoException, e:
        logging.warning("ParseInfoException: " + e.info)
        logging.info("Sleep:\t" + str(conf.waitTime))
        print "ParseInfoException: " + e.info
        print "Sleep:\t" + str(conf.waitTime)
        print url
        time.sleep(conf.waitTime)
        try:
            print "relogin"
            logging.info("relogin")
            cookie = login.weiboLogin()
            HEADERS = {"cookie": cookie}
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read() 
            if parser.errorPage(page) == True:
                logging.warning("Get error page " + url)
                print "Get error page " + url
                return "error"
            newUrl = parser.resetUrl(page)
            if newUrl != None:
                url = newUrl
                req = urllib2.Request(url, headers=HEADERS)
                page  = urllib2.urlopen(req).read() 

            info = parser.parseInfo(page)
        except Exception, e:
            logging.warning(e)
            logging.info(url)
            print e
            print url
            return None
    except exception.WriteInfoException, e:
        logging.warning("WriteInfoException: " + e.info)
        print "WriteInfoException: " + e.info

    logging.info("Info written")
    return info

def personalInfoCrawler(userID, domain, cookie, logPath):
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}

    count = 1
    timesToWait = 1 #the times of conf.waitTime to wait
    url = "http://www.weibo.com/p/" + domain + userID + "/info"
    while(count > 0):
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read() 
        except socket.error as e:
            if count < 1:
                return False
            logging.warning(e)
            print e
            if e.errno == errno.ECONNREFUSED: #when sina.com has detected the crawling, wait for enough time to reconnect
                timesToWait = timesToWait * 2;
                logging.info("Sleep:\t" + str(timesToWait * conf.waitTime)) #'timesToWait' times of the conf.waitTime
                print "Sleep:\t" + str(timesToWait * conf.waitTime)
                time.sleep(timesToWait * conf.waitTime)
                count = count - 1
                continue
        except Exception, e:
            logging.warning(e)
            print e
            return False
        count = count - 1
    
    try:
        parser.parsePersonalInfo(page, userID)
        logging.info("PersonalInfo Written")
    except exception.WriteInfoException, e:
        logging.warning("WriteInfoException: " + e.info)
        print "WriteInfoException: " + e.info
        return False

    return True
 

def fansCrawler(userID, domain, cookie,logPath):
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}

    pageCount = 1
    totalPage = 10
    flag = True #only to get the total page number one time
    count = 1
    timesToWait = 1 #the times of conf.waitTime to wait
    while pageCount <= totalPage: #Sina only allow 10 pages for us to see
        url = "http://www.weibo.com/p/" + domain + userID + "/follow?relate=fans&page=" + str(pageCount)
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except socket.error as e:
            if count < 1:
                return None
            logging.warning(e)
            print e
            if e.errno == errno.ECONNREFUSED: #when sina.com has detected the crawling, wait for enough time to reconnect
                timesToWait = timesToWait * 2;
                logging.info("Sleep:\t" + str(timesToWait * conf.waitTime)) #'timesToWait' times of the conf.waitTime
                print "Sleep:\t" + str(timesToWait * conf.waitTime)
                time.sleep(timesToWait * conf.waitTime)
                count = count - 1
                continue
        except Exception, e:
            logging.warning(e)
            logging.info("Sleep:\t" + str(conf.waitTime))
            print e
            print url
            print "Sleep:\t" + str(conf.waitTime)
            time.sleep(conf.waitTime)
            continue

        if flag:
            temp = parser.getNum(page, 1)
            total = 0
            if temp != None:
                total = int(temp)
            if total <= 180:
                totalPage = total / 20 + 1
            flag = False

        try:
            if not parser.parseFans(page, userID):
                logging.info(url)
                print url
                break
            else:
                #print url
                logging.info("Page " + str(pageCount) + " Fans written!")
                print "Page " + str(pageCount) + " Fans written!"
                pageCount += 1
        except exception.CookieExpiredException, e:
            logging.info(url)
            logging.warning("CookieExpiredException: " + e.info)
            logging.info("Sleep:\t" + str(conf.waitTime))
            print url
            print "CookieExpiredException: " + e.info
            print "Sleep:\t" + str(conf.waitTime)
            time.sleep(conf.waitTime)
            cookie = login.weiboLogin()#coolie expired, loin again
            if not cookie:
                logging.error("failed to relogin")
                print "failed to relogin"
                return False
            HEADERS = {"cookie": cookie}
            continue
        except exception.WriteInfoException, e:
            logging.error("WriteInfoException: " + e.info)
            print "WriteInfoException: " + e.info
            return False
   
    return True
    
def followCrawler(userID, domain, cookie,logPath):
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}

    pageCount = 1
    totalPage = 10
    flag = True #only to get the total page number one time
    count = 1
    timesToWait = 1 #the times of conf.waitTime to wait
    while pageCount <= totalPage: #Sina only allow 10 pages for us to see
        url = "http://www.weibo.com/p/" + domain + userID + "/follow?page=" + str(pageCount);
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except socket.error as e:
            if count < 1:
                return None
            logging.warning(e)
            print e
            if e.errno == errno.ECONNREFUSED: #when sina.com has detected the crawling, wait for enough time to reconnect
                timesToWait = timesToWait * 2;
                logging.info("Sleep:\t" + str(timesToWait * conf.waitTime)) #'timesToWait' times of the conf.waitTime
                print "Sleep:\t" + str(timesToWait * conf.waitTime)
                time.sleep(timesToWait * conf.waitTime)
                count = count - 1
                continue
        except Exception, e:
            logging.warning(e)
            logging.info("Sleep:\t" + str(conf.waitTime))
            print e
            print url
            time.sleep(conf.waitTime)
            continue
        
        if flag:
            temp = parser.getNum(page, 2)
            total = 0
            if temp != None:
                total = int(temp)
            if total <= 180:
                totalPage = total / 20 + 1
            flag = False

        try:
            if not parser.parseFollows(page, userID):
                logging.info(url)
                print url
                break
            else:
                #print url
                logging.info("Page " + str(pageCount) + " Follows written!")
                print "Page " + str(pageCount) + " Follows written!"
                pageCount += 1
        except exception.CookieExpiredException, e:
            logging.info(url)
            logging.warning("CookieExpiredException: " + e.info)
            logging.info("Sleep:\t" + str(conf.waitTime))
            print url
            print "CookieExpiredException: " + e.info
            print "Sleep:\t" + str(conf.waitTime)
            time.sleep(conf.waitTime)
            cookie = login.weiboLogin()#coolie expired, loin again
            if not cookie:
                logging.error("failed to relogin")
                print "failed to relogin"
                return False
            HEADERS = {"cookie": cookie}
            continue
        except exception.WriteInfoException, e:
            logging.error("WriteInfoException: " + e.info)
            print "WriteInfoException: " + e.info
            return False
   
    return True
    
#To extract necessary info for next request, 'api' control the page encoding type, 'rec' control recursive call for one time
def getWeiboUrlInfo(cookie, url, api, rec, logPath):
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie} 
    try:
        req = urllib2.Request(url, headers=HEADERS)
        page  = urllib2.urlopen(req).read()
    except Exception, e:
        logging.warning(e)
        logging.info("Sleep:\t" + str(conf.waitTime))
        print e
        print url
        print "Sleep:\t" + str(conf.waitTime)
        time.sleep(conf.waitTime)
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except Exception, e:
            logging.warning(e)
            logging.info(url)
            print e
            print url
            return None

    if api == 1:
        page = decodeASCII(page)
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    pat = re.compile(r'action-type=\\\"feed_list_item\\\"  mid=\\\"([^\"]*)\\\"')
    flag = False
    max_id = ""
    end_id = ""
    for n in pat.finditer(page):
        if not flag:
            end_id = n.group(1)
            flag = True
        max_id = n.group(1)
    
    if not flag:
        if api == 1 and rec == False:
            logging.warning("Failed to get UrlInfo, try another url")
            print "Failed to get UrlInfo, try another url"
            url = url.replace("&is_search=0&visible=0&is_tag=0&profile_ftype=1", "")
            return getWeiboUrlInfo(cookie,url,api,True, logPath)
        else:
            logging.warning("Failed to get UrlInfo!")
            print "Failed to get UrlInfo!"
            return None
        
    return {"max_id":max_id,"end_id":end_id, "page":page}

#解密ascii用到的函数
def toChar(str):
    if not str[0:2] == r'\u':
        return str
    code = 0
    i = 2
    while i < len(str):
        cc = ord(str[i])
        if cc >= 0x30 and cc <= 0x39:
            cc = cc - 0x30
        elif cc >= 0x41 and cc <=0x5AL:
            cc = cc - 0x41 + 10
        elif cc >= 0x61 and cc <= 0x7A:
            cc = cc - 0x61 + 10
        code <<= 4
        code += cc
        i += 1
    if code < 0xff:
        return str
    return unichr(code)

#解密被ascii加密的html
def decodeASCII(page):
    output = ""
    posFrom = 0
    posTo = page.find(r'\u',posFrom)
    while posTo >= 0:
        output += page[posFrom:posTo]
        output += toChar(page[posTo:posTo+6])
        posFrom = posTo + 6
        posTo = page.find(r'\u',posFrom)
    output += page[posFrom]
    return output
    
def weiboCrawler(cookie,info,logPath):  
    logging.basicConfig(filename=logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG) 
    domain = info["domain"]
    idstr = "" + domain + info["id"]

    #微博第一页获取Url信息    
    weiboUrl = "http://weibo.com/" + info['id']

    pageCount = 1
    weiboNum = int(info["weiboNum"])
    totalPage = weiboNum / 46 + 1
    if totalPage > conf.maxWeiboPage: #Only crawl the recent 460 weibos of the user defaultly
        totalPage = conf.maxWeiboPage
    while weiboNum != 0 and pageCount <= totalPage:
        #微博页面需要动态加载两次
        postfix = "/weibo?is_search=0&visible=0&is_tag=0&profile_ftype=1&page=%u#feedtop"%(pageCount) #微博每一页的后缀
        firstWeiboUrl = weiboUrl + postfix
        print firstWeiboUrl
        secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False,logPath) 
        if secondUrlInfo == None:
            postfix = "/mblog?is_search=0&visible=0&is_tag=0&profile_ftype=1&page=%u#feedtop"%(pageCount)
            firstWeiboUrl = weiboUrl + postfix
            print firstWeiboUrl
            secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False,logPath) 
            if secondUrlInfo == None:
                postfix = "/feed?is_search=0&visible=0&is_tag=0&profile_ftype=1&page=%u#feedtop"%(pageCount)
                firstWeiboUrl = weiboUrl + postfix
                print firstWeiboUrl
                secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False,logPath)
                if secondUrlInfo == None:
                    logging.warning("Failed to get weibos, skip " + info["id"])
                    logging.info(firstWeiboUrl)
                    print "Failed to get weibos, skip " + info["id"]
                    return "skip" #skip the user

        #微博的内容
        try:
            weiboList = parser.parseWeibo(secondUrlInfo["page"],info["id"],1) 
            for item in weiboList:
                zanCrawler(item["weiboID"], item["userID"], item["zanNum"], cookie)
                logging.info("zan written")
                print "zan written"
                repostCrawler(item["weiboID"], item["userID"], item["repostNum"], cookie)
                logging.info("repost written")
                print "repost written"
                commentCrawler(item["weiboID"], item["userID"], item["commentNum"], cookie)
                logging.info("comment written")
                print "comment written"
                
        except exception.CookieExpiredException, e:
            logging.info(firstWeiboUrl)
            logging.warning("CookieExpiredException: " + e.info)
            logging.info("Sleep:\t" + str(conf.waitTime))
            print firstWeiboUrl
            print "CookieExpiredException: " + e.info
            print "Sleep:\t" + str(conf.waitTime)
            time.sleep(conf.waitTime)
            cookie = login.weiboLogin()#coolie expired, loin again
            if not cookie:
                logging.error("failed to relogin")
                print "failed to relogin"
                return False
            HEADERS = {"cookie": cookie}
            continue
    
        if weiboNum - (pageCount-1)*46 > 16:
            max_id = secondUrlInfo["max_id"]
            end_id = secondUrlInfo["end_id"]
            pre_page = pageCount
            pagebar = 0
            secondWeiboUrl = "http://www.weibo.com/p/aj/mblog/mbloglist?domain=%s&pre_page=%u&page=%u&max_id=%s&end_id=%s&count=15&pagebar=%u&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__11&id=%s&script_uri=/p/%s/weibo&feed_type=0&is_search=0&visible=0&is_tag=0&profile_ftype=1"%(domain, pre_page, pageCount, max_id, end_id, pagebar, idstr, idstr)    
            print secondWeiboUrl
            thirdUrlInfo = getWeiboUrlInfo(cookie, secondWeiboUrl, 1, False, logPath)

            #微博的内容
            if thirdUrlInfo != None:
                weiboList = parser.parseWeibo(thirdUrlInfo["page"],info["id"],2)
                for item in weiboList:
                    zanCrawler(item["weiboID"], item["userID"], item["zanNum"], cookie)
                    logging.info("zan written")
                    print "zan written"
                    repostCrawler(item["weiboID"], item["userID"], item["repostNum"], cookie)
                    logging.info("repost written")
                    print "repost written"
                    commentCrawler(item["weiboID"], item["userID"], item["commentNum"], cookie)
                    logging.info("comment written")
                    print "comment written"
            
        if weiboNum - (pageCount-1)*46 > 26 and thirdUrlInfo != None:
            max_id = thirdUrlInfo["max_id"]
            end_id = thirdUrlInfo["end_id"]
            pre_page = pageCount
            pagebar = 1
            thirdWeiboUrl = "http://www.weibo.com/p/aj/mblog/mbloglist?domain=%s&pre_page=%u&page=%u&max_id=%s&end_id=%s&count=15&pagebar=%u&max_msign=&filtered_min_id=&pl_name=Pl_Official_LeftProfileFeed__11&id=%s&script_uri=/p/%s/weibo&feed_type=0&is_search=0&visible=0&is_tag=0&profile_ftype=1"%(domain, pre_page, pageCount, max_id, end_id, pagebar, idstr, idstr)
            print thirdWeiboUrl
           
            HEADERS = {"cookie": cookie}
            try:
                req = urllib2.Request(thirdWeiboUrl, headers=HEADERS)
                page  = urllib2.urlopen(req).read()
            except Exception, e:
                logging.warning(e)
                logging.info("Sleep:\t" + str(conf.waitTime))
                print e
                print thirdWeiboUrl
                print "Sleep:\t" + str(conf.waitTime)
                time.sleep(conf.waitTime)
                try:
                    req = urllib2.Request(thirdWeiboUrl, headers=HEADERS)
                    page  = urllib2.urlopen(req).read()
                except Exception, e:
                    logging.warning(e)
                    logging.info(thirdWeiboUrl)
                    print e
                    print thirdWeiboUrl
                    return False

            page = decodeASCII(page)    
            reload(sys)
            sys.setdefaultencoding('utf-8')
           
            #微博的内容
            weiboList = parser.parseWeibo(page,info["id"],3)
            for item in weiboList:
                zanCrawler(item["weiboID"], item["userID"], item["zanNum"], cookie)
                logging.info("zan written")
                print "zan written"
                repostCrawler(item["weiboID"], item["userID"], item["repostNum"], cookie)
                logging.info("repost written")
                print "repost written"
                commentCrawler(item["weiboID"], item["userID"], item["commentNum"], cookie)
                logging.info("comment written")
                print "comment written"

        logging.info("weibo page " + str(pageCount))
        print "weibo page " + str(pageCount) + "\n"
        pageCount += 1

    return True

def zanCrawler(weiboID, userID, zanNum, cookie):
    HEADERS = {"cookie": cookie} 
    totalPage = (int(zanNum) / 30) + 1
    if totalPage > conf.maxZanPage:
        totalPage = conf.maxZanPage
    zanUrl = "http://weibo.com/aj/like/big?_wv=5&mid=" + weiboID + "&page="
    pageCount = 1
    while pageCount <= totalPage:
        url = zanUrl + str(pageCount)
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except Exception, e:
            print e
            logging.warning("Cannot get zanIDs")
            return False
        parser.parseZan(page, userID, weiboID)
        pageCount += 1
    return True

def repostCrawler(weiboID, userID, repostNum, cookie):
    HEADERS = {"cookie": cookie}
    totalPage = (int(repostNum) / 20) + 1
    if totalPage > conf.maxRepostPage:
        totalPage = conf.maxRepostPage
    repostUrl = "http://weibo.com/aj/mblog/info/big?_wv=5&id=" + weiboID + "&page="
    pageCount = 1
    while pageCount <= totalPage:
        url = repostUrl + str(pageCount)
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except Exception, e:
            print e
            logging.warning("Cannot get repostIDs")
            return False
        parser.parseRepost(page, userID, weiboID)
        pageCount += 1

    return True

def commentCrawler(weiboID, userID, commentNum, cookie):
    HEADERS = {"cookie": cookie}
    totalPage = (int(commentNum) / 20) + 1
    if totalPage > conf.maxCommentPage:
        totalPage = conf.maxCommentPage
    commentUrl = "http://weibo.com/aj/comment/big?_wv=5&id=" + weiboID + "&page="
    pageCount = 1
    while pageCount <= totalPage:
        url = commentUrl + str(pageCount)
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except Exception, e:
            print e
            logging.warning("Cannot get commentIDs")
            return False
        parser.parseComment(page, userID, weiboID)
        pageCount += 1

    return True


#爬取微博搜索结果,按照热门程度排序
def searchResultCrawler(cookie,keywords):
    HEADERS = {"cookie": cookie}
    url = "http://s.weibo.com/wb/%s&xsort=hot&page="%(keywords)
    totalPage = conf.maxSearchPage
    pageCount = 1
    count = 1 #The number of times for the crawler allowed to sleep
    while pageCount <= totalPage:
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
        except Exception, e:
            logging.warning("Sleep:\t" + str(conf.waitTime))
            print "Sleep:\t" + str(conf.waitTime)
            time.sleep(conf.waitTime)
            count -= 1
            if count < 0:
                return False
            continue
        try:
            parser.parseSearch(page, keywords)
        except Exception, e:
            print e
            logging.error("parseSearch exception")
            return False 
        pageCount += 1
    return True

#Read a candidateID to crawl and then remove it
lock = threading.Lock()
def readID():
    lock.acquire()
    startID = dbhandler.readCandidateID()
    while(startID != None and dbhandler.hasBeenProcess(startID)):
        dbhandler.removeCandidateID(startID)
        startID = dbhandler.readCandidateID()
    if not startID == None: 
        dbhandler.removeCandidateID(startID)
    lock.release()
    return startID


def mainCrawler(name, initial):
    logPath = conf.logPath
    logging.basicConfig(filename=logPath,format="%(threadName)s:%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)

    cookie = login.weiboLogin()
    if not cookie:
        print "cookie is None"
        return
    
    startID = readID()

    if startID == None:
        startID = conf.startID

    if conf.specificID != "":
        startID = conf.specificID

    errorBound = 20
    errorCount = errorBound #test whether getting error page continuously for 10 times
    relogin = conf.relogin
    while(startID != None):
        relogin -= 1
        if relogin < 0:
            print "System relogin"
            logging.info("System relogin")
            cookie = login.weiboLogin()
            relogin = conf.relogin
            if not cookie:
                print "cookie is none"
                return

        logging.info("ID:\t"+startID)
        
        if startID == conf.skipID:
            startID = readID()
            continue

        info = getInfo('http://www.weibo.com/u/' + startID, cookie, logPath)
        if info == None:
            logging.info("info: None\t" + startID)
            print "info: None\t" + startID
            logging.info("relogin")
            print "relogin"
            cookie = login.weiboLogin()
            startID = readID()
            continue

        if info == "error":
            errorCount -= 1
            if errorCount == 0:
                logging.error("Too many error pages")
                print "Too many error pages"
                return
            startID = readID()
            continue
        else:
            errorCount = errorBound

        if not personalInfoCrawler(info['id'], info['domain'], cookie, logPath):
            return
        if not fansCrawler(info['id'], info['domain'], cookie, logPath):
            return
        if not followCrawler(info['id'], info['domain'], cookie, logPath):
            return
        if not weiboCrawler(cookie, info, logPath):
            return

        if conf.specificID != "":
            break
        if initial:
            dbhandler.createIndex()
            break
    
        startID = readID() 

    logging.info("Finished! " + str(name))
    print "Finished! " + str(name)

def main():
    startID = dbhandler.readCandidateID()
    if startID == None or conf.specificID != "":
        mainCrawler("initial", True)
    if conf.specificID != "":
        return
    for i in range(conf.crawlerNum):
        nameStr = 'thread-' + str(i)
        threading.Thread(target = mainCrawler, args = ([nameStr, False]), name = nameStr).start()
    
    #cookie = login.weiboLogin()
    #searchResultCrawler(cookie, "找工作")

if __name__=='__main__':
    main()
