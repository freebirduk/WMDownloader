# WeatherManager

>
>This project is very early in development but some of it is now usable. The details below show what's done and what 
> is to come.

Weather Manager is a system to download, store and display Personal Weather Station (PWS) data from the 
Weather Underground (WU) website and, later to analyse that historical data. Why bother? WU after all stores your data and has some really useful tables and charts much of which is free. The reasons are these:

- We don't know what will happen to the data in the future. IBM may dump the WU product. The data may get watered 
  down, become fully chargeable or expensive. We just don't have control.
- The data retention period on WU is short for the free or cheap options. 
- The analytics are good but may not be all you want.

So Weather Manager will provide:

- WMDownloader - A program to access the WU API, retrieve and store your PWS data in a SQL database (SQL Server Express or other).
- WMPresenter - A weather offering analysis of the observations in your database. This will include the sort of 
  thing found in WU plus other analyses such as extremes e.g. "hottest March ever".

## WMDownloader - *Initial release now available*

This repository holds the function to download your WU data and store it in a database.

### Features:

- You'll probably set the program up to run automatically every day. It will try to download all observations not 
  already downloaded up until the previous day.
- It's designed to run quietly in the background. 
  If you miss scheduled runs the program will catch up for you automatically.
- A log file is kept to record successful downloads and any issues arising.
- Where warnings or errors occur you'll be sent an e-mail alert.
- The program will check that data is being recorded for the day it's running on. This gives you a heads-up if 
  perhaps your weather station batteries are dead or your wireless connection has failed. Again, you'll get a 
  warning e-mail.
- You can set a limit to the number of days that will be downloaded per run. This is helpful if you have a lot of 
  data already on WU and you want to avoid exceeding the WU API's throttling limit (currently about 2000 calls a day 
  I believe). The program makes one API call per day of data.

### Something to note:
WMDownloader will download observations up to and including *two days ago*. Why not up to yesterday? This is because 
the Weather Underground API can sometimes be delayed in serving up the full set of observations for yesterday, 
particularly if you make your request early in the day. By only downloading observations up to the day *before* 
yesterday a more complete dataset is achieved. 

### Configuration:

- Run the DatabaseInitialBuild.sql script on a MariaDb server to build the data repository. You can also use 
  DatabaseAddUser.sql to add a user.
- Rename the config-ChangeMe.ini file to config.ini
- Amend the values in config.ini to store your SQL Server details, Weather Underground API credentials and 
  e-mail credential. *These will not be encrypted so use caution as to where you locate things.*

### Coming next:

The next version will include the ability to alert you to weather extremes e.g. "Hottest ever day", "Driest August", 
etc. These extremes will be stored for WMPresenter to use. You'll also get an e-mail alert when an extreme has 
been exceeded.


# WMPresenter

Development hasn't started on this yet. It will likely be written as a desktop application using TKinter. A web 
version may follow later. 
