WeiboCrawler
============

To crawl information from sina weibo (http://weibo.com/)

##Why WeiboCrawler

Sina weibo is the largest website for people to share their ideas, photos and any other things with their friends in China just like Twitter. I write this program just to help me to do some research about social network. Please do not use the data for business.

##About the code

It's written in *python*. It's simple and multithreading. 

Once a userID is provided, the crawler can begin fetching information from *weibo.com*. It was designed to crawl the basic information, fans, followees and weibos of a user sequentially. 

##Data Format

All crawled data are stored in MongoDB. Five collections will automatically be created: **CandidtaeID**, **Fans**, **Follows**, **Info**, **ProcessedID**, **weibo**, **Comment**, **Zan**, **Repost**, **PersonalInfo** and **SearchResult**.
###CandidateID

Store the userIDs which will be crawled.

###ProcessedID

Store the userIDs which have been crawled.

###Fans

Store the fans of each user.

###Follows

Store the people the user has followed.

###Info

Store basic information of each user.

e.g. { "_id" : ObjectId("529c81b2c69256180c94640e"), "followNum" : "552", "domain" : "103505", "name" : "李开复", "level" : "12", "userID" : "1197161814", "fansNum" : "51780522", "weiboNum" : "13774" }

###weibo

Store the weibos of each user.

e.g. { "_id" : ObjectId("529c81d6c69256180c946711"), "zanNum" : "11813", "userID" : "1197161814", "repostNum" : "17037", "commentNum" : "34609", "wbText" : " <span class=\"W_ico20 ico_feedpin\"> </a>n                                    最近化疗后身体检查结果有几项指数未降反升，需要更加严格的遵照医嘱，专注于治疗和休养。不得不大幅度减少在社交媒体上的时间。很遗憾。 ", "repostText" : "", "time" : "2013-10-21 09:09" }

###Comment

Store the userIDs of comments of each weibo. Each document will store about 26 ids.

e.g. { "_id" : ObjectId("52d93465c692563c6ae727cb"), "weiboID" : "3666951488320239", "userID" : "1197161814", "commentIDs" : "1998324642:2176595717:2809284650:2280850905:1038180055:1567572731:1612228495:1735696757:1299876663:1775671684:2053129710:3613006151:2971376255:1653872002:1953746532:1923752952:1234704932:2365281923:2218573275:1625712021:1576214400:1696716502:2970752802:1625712021:1696716502:" }

###Repost

Store the userIDs of reposts of each weibo. Each document will store about 26 ids.

###Zan

Store the userIDs of "赞" of each weibo.

###PersonalInfo

Store the data crawled from the personal information page.

e.g. { "_id" : ObjectId("52d8d83ec692561c2798b18d"), "WorkInfo" : "", "RegistTime" : "2011-02-22", "UserID" : "1234139811", "sex" : "女", "SelfIntroduction" : "做努力而温暖的人！", "NickName" : "悠然的绿", "EducationInfo" : "", "Tags" : "", "Birthday" : "6月4日", "Address" : "江苏 苏州" }

###SearchResult

Store the data of the weibo search result.

e.g. { "_id" : ObjectId("52da22afc69256580ccf99af"), "keywords" : "找工作", "wbText" : "思想聚焦 ： 毕业后,好多事情都被颠覆了。原来校花也会变丑，原来上铺和下铺也能恋爱，原来 找工作 可以和专业无关,原来不是每个人都有资格被潜规则,原来大家对于未来都一样焦虑,原来不上课不考试真的拿不到学位证,原来第一份工作工资那么少,原来招聘会挤都挤不进去,原来毕了业嫁人也很难.原来，读书真好。——刘同 " }

##Quick Start

Make sure you have install mongodb and python in your machine before running the code.
* Start the service of mongodb
* Modify the configuration file(*conf.py*) if necessary. Please provide your username and password on *weibo.com*. The number of crawlers(threads) can also be set.
* Run the crawler in command line:    >>>>python crawler.py

The program will create a log file on your disk. When it starts running, it won't stop until all userIDs in **CandidateID** are crawled or error occurred. If you force to stop the program and restart it, you will lost some data of the user whom is being crawled(it won't re-crawled the information of the unfinished user). 

##More Infomation

At present the crawler is only able to crawl the characters of the weibo content. It can't crawl the image or videos. The *searchResultCrawler* are not allowed to run defaultly. You may run it in yonr program if needed. At present I am still not very good at handling the exceptions in my program and I will try my best to make crawler more effient in the future. 
If you have any questions or suggestions, feel free to contact me
(shaoyf2011@gmail.com).
