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

def getInfo(url, cookie):
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}
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
    except Exception, e:
        logging.warning(e)
        print e
        return None
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
            logging.warning("ParseInfoException: " + e.info)
            logging.info(url)
            print "ParseInfoException: " + e.info
            print url
            return None
    except exception.WriteInfoException, e:
        logging.warning("WriteInfoException: " + e.info)
        print "WriteInfoException: " + e.info

    logging.info("Info written")
    return info

def personalInfoCrawler(cookie):
    pass 

def fansCrawler(userID, domain, cookie):
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}

    pageCount = 1
    totalPage = 10
    flag = True #only to get the total page number one time
    while pageCount <= totalPage: #Sina only allow 10 pages for us to see
        url = "http://www.weibo.com/p/" + domain + userID + "/follow?relate=fans&page=" + str(pageCount)
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
    
def followCrawler(userID, domain, cookie):
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    HEADERS = {"cookie": cookie}

    pageCount = 1
    totalPage = 10
    flag = True #only to get the total page number one time
    while pageCount <= totalPage: #Sina only allow 10 pages for us to see
        url = "http://www.weibo.com/p/" + domain + userID + "/follow?page=" + str(pageCount);
        try:
            req = urllib2.Request(url, headers=HEADERS)
            page  = urllib2.urlopen(req).read()
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
def getWeiboUrlInfo(cookie,url,api, rec):
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
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
            return getWeiboUrlInfo(cookie,url,api,True)
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
    
def weiboCrawler(cookie,info):  
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG) 
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
        secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False) 
        if secondUrlInfo == None:
            postfix = "/mblog?is_search=0&visible=0&is_tag=0&profile_ftype=1&page=%u#feedtop"%(pageCount)
            firstWeiboUrl = weiboUrl + postfix
            print firstWeiboUrl
            secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False) 
            if secondUrlInfo == None:
                postfix = "/feed?is_search=0&visible=0&is_tag=0&profile_ftype=1&page=%u#feedtop"%(pageCount)
                firstWeiboUrl = weiboUrl + postfix
                print firstWeiboUrl
                secondUrlInfo = getWeiboUrlInfo(cookie, firstWeiboUrl, 0, False)
                if secondUrlInfo == None:
                    logging.warning("Failed to get weibos, skip " + info["id"])
                    logging.info(firstWeiboUrl)
                    print "Failed to get weibos, skip " + info["id"]
                    return "skip" #skip the user

        #微博的内容
        try:
            parser.parseWeibo(secondUrlInfo["page"],info["id"],1) 
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
            thirdUrlInfo = getWeiboUrlInfo(cookie, secondWeiboUrl, 1, False)

            #微博的内容
            if thirdUrlInfo != None:
                parser.parseWeibo(thirdUrlInfo["page"],info["id"],2)
            
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
            parser.parseWeibo(page,info["id"],3)

        logging.info("weibo page " + str(pageCount))
        print "weibo page " + str(pageCount) + "\n"
        pageCount += 1

    return True


def weiboCommentCrawler(page):
    #获取第一个微博的评论Url
    pat_mid = re.compile(r'action-type=\\\"feed_list_item\\\"  mid=\\\"([^\"]*)\\\"')
    for n in pat_mid.finditer(page):
        tempUrl = "http://weibo.com/aj/comment/small?_wv=5&act=list&mid="+n.group(1)+"&uid=1817254035&isMain=true&ouid="+info["id"]+"&location=page_"+info["domain"]+"_home&_t=0&__rnd="
        req = urllib2.Request(tempUrl, headers=HEADERS)
        page  = urllib2.urlopen(req).read()
        
        pat_commentId = re.compile(r'\\u8bba\\uff0c<a href=\\\"\\/'+info["id"]+r'\\([^\\]*)\\\">\\u70b9\\u51fb\\')
        r_commentId = pat_commentId.search(page)
        print n.group(1),r_commentId.group(1)



#爬取微博搜索结果
def searchResultCrawler(cookie,keywords):
    url = "http://s.weibo.com/weibo/%s&page="%(keywords)
    url += "1"
    HEADERS = {"cookie": cookie}
    req = urllib2.Request(url, headers=HEADERS)
    page  = urllib2.urlopen(req).read()
    return



def main():
    logging.basicConfig(filename=conf.logPath,format="%(asctime)s:%(levelname)s:%(message)s",level=logging.DEBUG)
    cookie = login.weiboLogin()
    if not cookie:
        print "cookie is none"
        return

    startID = dbhandler.readCandidateID()
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
            if not cookie:
                print "cookie is none"
                return

        logging.info("ID:\t"+startID)
        
        if startID == conf.skipID:
            dbhandler.removeCandidateID(startID)
            startID = dbhandler.readCandidateID()
            continue

        if dbhandler.hasBeenProcess(startID):
            dbhandler.removeCandidateID(startID)
            startID = dbhandler.readCandidateID()
            if startID == None:
                break;
            continue

        info = getInfo('http://www.weibo.com/u/' + startID, cookie)
        if info == None:
            dbhandler.removeCandidateID(startID)
            startID = dbhandler.readCandidateID()
            continue

        if info == "error":
            errorCount -= 1
            if errorCount == 0:
                logging.error("Too many error pages")
                print "Too many error pages"
                return
            dbhandler.removeCandidateID(startID)
            startID = dbhandler.readCandidateID()
            continue
        else:
            errorCount = errorBound

        if not fansCrawler(info['id'], info['domain'], cookie):
            return
        if not followCrawler(info['id'], info['domain'], cookie):
            return
        if weiboCrawler(cookie, info) == False:
            return

        dbhandler.removeCandidateID(startID)
        startID = dbhandler.readCandidateID()
        if conf.specificID != "":
            break

    logging.info("Finished!")
    print "Finished!"
        

if __name__=='__main__':
    main()
