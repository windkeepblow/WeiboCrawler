# -*- coding: utf-8 -*- 
import urllib2
import urllib
import base64
import binascii
import getpass
import requests
import json
import cookielib
import rsa
import re
import conf
#密码加密rsa
def encrypt_passwd(password, pubkey, servertime, nonce):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)#创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    return passwd


#模拟登录,获取cookie
def weiboLogin():     
    username = conf.username
    username = urllib.quote(username)
    username = base64.encodestring(username)[:-1]
    
    #password = getpass.getpass('Please enter weibo passwd: ') 
    password = conf.pwd

    #发送请求
    WBCLIENT = 'ssologin.js(v1.4.11)'
    user_agent = ('Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11')

    session = requests.session()
    session.headers['User-Agent'] = user_agent
    
    #获取信息
    resp = session.get('http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=%s'%(username, WBCLIENT))
     
    pre_login_str = re.match(r'[^{]+([^)]*)',resp.content).group(1)
    pre_login = json.loads(pre_login_str)
  
    data = {
         'entry': 'weibo',
         'gateway' : 1,
         'from' : '',
         'savestate' : 7,
         'userticket' : 1,
         'ssosimplelogin' : 1,
         'su' : username,
         'service' : 'miniblog',
         'servertime': pre_login['servertime'],
         'nonce': pre_login['nonce'],
         'vsnf': 1,
         'vsnval': '',
         'pwencode': 'rsa2',
         'sp': encrypt_passwd(password, pre_login['pubkey'],
                         pre_login['servertime'], pre_login['nonce']),
         'rsakv' : pre_login['rsakv'],
         'encoding': 'UTF-8',
         'prelt': '115',
         'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.si'
                'naSSOController.feedBackUrlCallBack',
         'returntype': 'META'
    }     
    resp = session.post(
        'http://login.sina.com.cn/sso/login.php?client=%s'%(WBCLIENT),
        data=data
    )
    
    retcode =re.search(r'&retcode=([\d]*)\"',resp.content)
    if not retcode or retcode.group(1) is not '0':
        print "登录失败"
        return None

    login_url = re.search(r'replace\([\"\']([^\'\"]+)[\"\']',resp.content).group(1)

    request = urllib2.Request(login_url)

    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    opener.open(request)
    
    pat = re.compile(r'<Cookie ([^\s]*) for ')
    cookie = ""
    for n in pat.finditer(str(cookiejar)):
        cookie = cookie + str(n.group(1)) + "; "       
    return cookie