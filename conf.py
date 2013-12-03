##Configration file of weibo crawler

database = "weibodb" #The name of the database
waitTime = 30 #When reach the request limit, how many seconds will the program wait for
logPath = "WeiboCrawler.log"
startID = "1197161814" #From which user to begin crawling, "kaifulee"
maxWeiboPage = 10 #Only to crawl the recent 10 pages(num: 460) weibo of the user

username = "" #user name of weibo to login
pwd = "" #password of weibo to login

#optional
skipID = "" #To skip specific ID
specificID = "" #Only to crawl this ID
