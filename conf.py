##Configration file of weibo crawler

database = "weibodb" #The name of the database
waitTime = 600 #When reach the request limit, how many seconds will the program wait for
startID = "1197161814" #From which user to begin crawling, "kaifulee"
maxWeiboPage = 10 #Only to crawl the recent 10 pages(num: 460) weibo of the user
relogin = 100 #After how many iterations for the crawler to relogin
crawlerNum = 1 #the number of crawlers(threads)
logPath = "WeiboCrawler.log" #The path of the log file

username = "shaoyf2013@163.com"  #user name of weibo to login
pwd = "aa123456" #password of weibo to login

#optional
skipID = "" #To skip specific ID
specificID = "" #Only to crawl this ID
