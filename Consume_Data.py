import socket
import json
from datetime import datetime, time
import sqlite3

# Create Database
conn = sqlite3.connect("snagdb.db")
cursorObj = conn.cursor()

# Create Table
cursorObj.execute("create table if not exists snag_evt_history (userid String, mouse_avg Float, key_avg Float, page_load_avg Float);")
    
# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = socket.gethostname()                           

# bind the socket to the port 23456, and connect
server_address = ("localhost", 8889)  
sock.connect(server_address)                              
print ("Consuming Data")

# Receive no more than 1024 bytes
while(True):
    msg = sock.recv(1024)                                     
    data=msg.decode()
    data=json.loads(data)

# Rule Engine Based Bot Score calculation
    userid=data['userid']
    number_of_events=len(data['Events'])
    mouse_time_total=0
    key_stroke_total=0
    page_load_total=0
    total_score=38
    bot_score=0
    firstpage=True
    cursorObj = conn.cursor()
    
# Adding different Event variables
    for eachEvent in data['Events']:
        mouse_time_total=mouse_time_total+int(eachEvent['mousetime'])
        key_stroke_total=key_stroke_total+int(eachEvent['keystroke'])
        if (firstpage):
            temp_ts=eachEvent['signalts']
            firstpage=False
        else:
            date_h=datetime.strptime(eachEvent['signalts'], '%Y-%m-%d %H:%M:%S')
            date_l=datetime.strptime(temp_ts, '%Y-%m-%d %H:%M:%S')
            timediff=date_h-date_l
            page_load_total=page_load_total+timediff.seconds + timediff.days * 86400

# Finding average for different events
    mouse_avg=(mouse_time_total/number_of_events)
    key_avg=(key_stroke_total/number_of_events)
    page_load_avg=(page_load_total/number_of_events)
    
#Scoring the Mouse Event
    if ((mouse_avg > 0) & (mouse_avg <= 20)):
        bot_score = bot_score+1
    elif (mouse_avg < 50):
        bot_score = bot_score+2
    elif (mouse_avg < 200):
        bot_score = bot_score+3
    elif (mouse_avg > 200):
        bot_score = bot_score+4

#Scoring the Keystroke Event
    if ((key_avg > 0) & (key_avg < 5)):
        bot_score = bot_score+10
    elif (key_avg <= 10):
        bot_score = bot_score+20
    elif (key_avg > 10):
        bot_score = bot_score+30

#Scoring the Page Load Time Event
    if ((page_load_avg > 0) & (page_load_avg < 21)):
        bot_score = bot_score+1
    elif (page_load_avg < 50):
        bot_score = bot_score+2
    elif (page_load_avg < 200):
        bot_score = bot_score+3
    elif (page_load_avg > 200):
        bot_score = bot_score+4

#Scoring the Event - Bot Score
    botscore_final = (bot_score/total_score)
    
# History data validation

    record=(userid,mouse_avg,key_avg,page_load_avg)
    
    cursorObj.execute("select * from snag_evt_history where userid = '%s' ;" % userid)
    rows = cursorObj.fetchall()
    for row in rows:
        user_name, mouse_val, key_val, page_val = row

    if (len(rows)==0):
        cursorObj.execute("insert into snag_evt_history (userid, mouse_avg, key_avg, page_load_avg) values (?, ?, ?, ?);", record)
        conn.commit()
        if (botscore_final <0.5):
            print("User  '%s' is BOT" % (userid))
        else:
            print("User  '%s' is Human " % (userid))
    else:
        page_load_ratio=(page_val-page_load_avg)/page_load_avg
        if page_load_ratio < 0:
            page_load_ratio = page_load_ratio * -1
        if( (mouse_val==mouse_avg) & (key_val==key_avg) & (page_load_ratio < .1)):
            print("User  '%s' is BOT Macro" % (userid))
        else:
            print("User  '%s' is Human - Recurring " % (userid))

    cursorObj.close()

sock.close()
print ("Closed")


