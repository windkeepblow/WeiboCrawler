WeiboCrawler
============

To crawl information from sina weibo (http://weibo.com/)

##Why WeiboCrawler

Sina weibo is the largest website for people to share their ideas, photos and any other things with their friends in China just like Twitter. I write this program just to help me to do some research about social network. Please do not use the data for business.

##About the code

It's written in *python*. It's simple and multithreading. 

Once a userID is provided, the crawler can begin fetching information from *weibo.com*. It was designed to crawl the basic information, fans, followees and weibos of a user sequentially. 

##Data Format

All crawled data are stored in MongoDB. Five collections will automatically be created: **CandidtaeID**, **Fans**, **Follows**, **Info**, **ProcessedID** and **weibo**.
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

##Quick Start

Make sure you have install mongodb and python in your machine before running the code.
* Start the service of mongodb
* Modify the configuration file(*conf.py*) if necessary. Please provide your username and password on *weibo.com*. The number of crawlers(threads) can also be set.
* Run the crawler in command line:    >>>>python crawler.py

The program will create a log file on your disk. When it starts running, it won't stop until all userIDs in **CandidateID** are crawled or error occurred. If you force to stop the program and restart it, you will lost some data of the user whom is being crawled(it won't re-crawled the information of the unfinished user). 

##More Infomation

At present the crawler is only able to crawl the characters of the weibo content. It can't crawl the image or videos. The *weiboCommentCrawler* and *searchResultCrawler* are also unavailable. I will try to make them work in the future.
If you have any questions or suggestions, feel free to contact me
(shaoyf2011@gmail.com).
