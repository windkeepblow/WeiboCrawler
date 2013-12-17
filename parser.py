# -*- coding: utf-8 -*- 
import re
import dbhandler
import exception
#Get user's name, id, level, ...(Not necessary to login)
def parseInfo(page):
	#找出用户名
    pat_name = re.compile(r'\$CONFIG\[\'onick\'\]=\'([^\']*)\'')
    r_name = pat_name.search(page)    
    #用户ID
    pat_id = re.compile(r'\$CONFIG\[\'oid\'\]=\'([^\']*)\'')
    r_id = pat_id.search(page)
    #用户域 
    pat_domain = re.compile(r'\$CONFIG\[\'domain\'\]=\'([^\']*)\'')
    r_domain = pat_domain.search(page)
     #用户等级  
    #pat_level = re.compile(r'title=\\\"([^\d]*)([\d]*)\\\" levelcard=')
    pat_level = re.compile(r'class=\\\"W_level_num l([\d]*)\\\"')
    r_level = pat_level.search(page)
    #用户关注
    pat_follow = re.compile(r'<strong node-type=\\\"follow\\\">([^<]*)<')
    r_follow = pat_follow.search(page)
    #用户粉丝
    pat_fans = re.compile(r'<strong node-type=\\\"fans\\\">([^<]*)<')
    r_fans = pat_fans.search(page)
    #用户微博    
    pat_weibo = re.compile(r'<strong node-type=\\\"weibo\\\">([^<]*)<')
    r_weibo = pat_weibo.search(page)

    fansNum = None
    followNum = None
    weiboNum = None
    if r_follow == None or r_fans == None or r_weibo == None:
        pat = re.compile(r'S_line1\\\"[^>]*>[^<]*<strong class=[^>]*>([\d]+)<')
        
        list = pat.findall(page)
        if len(list) == 0:
            pat = re.compile(r'S_func1\\\"[^>]*>[^<]*<strong class=[^>]*>([\d]+)<')
            list = pat.findall(page)

        try: 
            followNum = list[0]
            fansNum = list[1]
            weiboNum = list[2]
        except Exception, e:
            print e
            raise exception.ParseInfoException("Failed to get followNum, fansNum, or weiboNum!")
            return None
    else:
        followNum = r_follow.group(1)
        fansNum = r_fans.group(1)
        weiboNum = r_weibo.group(1)
    
    if r_name and r_id and r_domain and r_level and followNum and fansNum and weiboNum:
        info = {
            "name":r_name.group(1),
            "id":r_id.group(1),
            "domain":r_domain.group(1),
            "level":r_level.group(1),
            "followNum":followNum,
            "fansNum":fansNum,
            "weiboNum":weiboNum
        }
    else:
        raise exception.ParseInfoException("Failed to get Info!")
        return None
 
    print "name =", info["name"], "\nid =", info["id"], "\ndomain =", info['domain']
    print "followNum =", info["followNum"]
    print "fansNum =", info["fansNum"]
    print "weiboNum =", info["weiboNum"]
    print "level =", info["level"]
    
    try: 
        dbhandler.writeInfo(info)
    except Exception, e:
        print e    
        raise exception.WriteInfoException("Failed to write Info!")
        return None

    return info

#Get the fan's ids of the user
def parseFans(page, userID):
    #To test whether the cookie is expired or reach the request limit
    pat_title = re.compile(r'<title>([^\<]*)的微博')
    title = pat_title.search(page)
    if not title:
        raise exception.CookieExpiredException("Wait and then login")
        return False

    #Extract the ids 
    pat_id = re.compile(r'\\\"itemClick\\\" action-data=\\\"uid=([\d]*)&')
    list = pat_id.findall(page)
    if not list:
        print "Cannot get Fans!"
    try:
        dbhandler.writeFans(list, userID)
    except Exception, e:   
        print e
        raise exception.WriteInfoException("Failed to write Fans!")
        return False
    return True

    #Get the follow's ids of the user
def parseFollows(page, userID):
    #To test whether the cookie is expired or reach the request limit
    pat_title = re.compile(r'<title>([^\<]*)的微博')
    title = pat_title.search(page)
    if not title:
        raise exception.CookieExpiredException("Wait and then login")
        return False

    #Extract the ids 
    pat_id = re.compile(r'\\\"itemClick\\\" action-data=\\\"uid=([\d]*)&')
    list = pat_id.findall(page)
    if not list:
        print "Cannot get Follows!"
    try:
        dbhandler.writeFollows(list, userID)
    except Exception, e:   
        print e
        raise exception.WriteInfoException("Failed to write Follows!")
        return False
    return True

#To get the reset url
def resetUrl(page):
    pat_url = re.compile(r'location\.replace\(\"([^\"]+)\"\)')
    r_url = pat_url.search(page)
    if r_url == None:
        return None
    return r_url.group(1)

#get total number of fans, follows or weibos, api=1 fans, api=2 follows, api=3 weibo
def getNum(page, api):
    pat_fans = re.compile(r't_nums S_txt2\\\">[^已]*已有(\d+)人关注了')
    pat_follow = re.compile(r't_nums S_txt2\\\">[^<]+关注了(\d+)人')

    if api == 1:
        r_fans = pat_fans.search(page)
        if r_fans != None:
            return r_fans.group(1)
    if api == 2:
        r_follow = pat_follow.search(page)
        if r_follow != None:
            return r_follow.group(1)
    return None

def parseWeibo(page, userID, step):
    #To test whether the cookie is expired or reach the request limit
    if step == 1:
        pat_title = re.compile(r'<title>([^\<]*)的微博')
        title = pat_title.search(page)
        if not title:
            raise exception.CookieExpiredException("Wait and then login")
            return False

    pat_minfo = re.compile(r'(tbinfo)=\\\".*?(>.*?feed_list_repeat)')
    pat_weibo_text = re.compile(r'feed_list_content\\\".*?(>.*?<)\\/div>')
    pat_repost = re.compile(r'feed_list_reason\\\".*?(>.*?<)\\/div>')
    #pat_bottomInfo = re.compile(r'WB_func clearfix\\\".*?(>.*?feed_list_repeat)')
    pat_time = re.compile(r'WB_from.*?title=\\\"(.+?)\\\"')
    pat_zanNum = re.compile(r'W_ico20 icon_praised_b.*?em>(.*?)<')
    pat_commentNum = re.compile(r'fl_comment.*?>评论\((\d+)\)<')
    pat_repostNum = re.compile(r'fl_forward.*?>转发\((\d+)\)<')
    pat_info = re.compile(r'>(.+?)<')


    weiboList = []
    for minfo in pat_minfo.finditer(page):
        text = ""
        repost = ""
        time = ""
        zanNum = "0"
        commentNum = "0"
        repostNum = "0"
        wb_text = pat_weibo_text.search(minfo.group(2))
        wb_repost = pat_repost.search(minfo.group(2))

        for info in pat_info.finditer(wb_text.group(1)):
            text = text + info.group(1).strip("\\nt| ") + " "
            text = text.replace("\\","")

        if wb_repost != None:
            for info in pat_info.finditer(wb_repost.group(1)):
                repost = repost + info.group(1).strip("\\nt| ") + " "

        r_time = pat_time.findall(minfo.group(2))
        r_zanNum = pat_zanNum.findall(minfo.group(2))
        r_commentNum = pat_commentNum.search(minfo.group(2))
        r_repostNum = pat_repostNum.search(minfo.group(2))

        if len(r_time) == 2:
            time = r_time[1]
            zanNum = r_zanNum[1][1:-1]
        else:
            time = r_time[0]
            zanNum = r_zanNum[0][1:-1]

        zanNum = zanNum.strip();
        if zanNum == "":
            zanNum = "0"
        if r_commentNum != None:
            commentNum = r_commentNum.group(1)
        if r_repostNum != None:
            repostNum = r_repostNum.group(1)

        finalInfo = {
                "wbText":text,
                "repostText":repost,
                "time":time,
                "zanNum":zanNum,
                "commentNum":commentNum,
                "repostNum":repostNum}
        weiboList.append(finalInfo)

    dbhandler.writeWeibo(weiboList, userID)

    #for item in weiboList:
    #    print item["wbText"]
    #    print item["repostText"]
    #    print item["time"]
    #    print item["zanNum"]
    #    print item["commentNum"]
    #    print item["repostNum"]

    return True

#Test whether the specific user page is abnormal
def errorPage(page):
    pat_title = re.compile(r'<title>错误提示[^<]*</title>')
    r_title = pat_title.search(page)
    if r_title != None:
        return True
    return False
