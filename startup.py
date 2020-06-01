#!/usr/bin/env python
import subprocess
import board
import re
import time
import digitalio
import os
from os import listdir
from os.path import isfile
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create blank image for drawing. This type stuff comes from adafruit.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing. This type stuff comes from adafruit.
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 15)
enableADB = True
#enableADB = False

disableAd = True


#LOG IN INFO
AMAZON_EMAIL = ""
AMAZON_PASS = ""

WIFI_SSID=""
WIFI_PASS=""


deviceID = ""

#probably not the best way to go about this, but it'll be fixed....
def doCommNoCheck(command):
    print("COMMAND:  ", command)
    command = command.split(" ")
    proc = subprocess.run(command, stdout=subprocess.PIPE)
    #proc.wait()
    return proc.stdout.decode("utf-8")

def doComm(command):
    global deviceID
    
    #I honestly hate having to add an extra command in there every time,
    #but unfortunately it's the only way I can think of to make sure we're consistent
    # and not starting over in between devices, or starting mid way on a new device. Please let me know if you have an alternative.
    if (getDeviceID() == deviceID):
        return doCommNoCheck(command)
        
def getDeviceID():
    tid = doCommNoCheck("adb shell settings get secure android_id")
    print(tid)
    return(tid)

def updateDeviceID():
    global deviceID
    
    dev=getDeviceID()
    if ("error" not in dev):
        deviceID = dev
        
def clearDispContents():
    global oled
    global image
    global draw

    oled.fill(0)
    oled.show()
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

def showImage():
    global oled
    global image
    oled.image(image)
    oled.show()

#Puts out text to the specified line, starting from 0.
def outText(text, line, font):
    global draw
    draw.text((0, 14*line), text, font=font, fill=128)


def checkDevice():
    clearDispContents()
    outText("Wait for Device", 0, font1)
    outText("(check debug)", 1, font1)
    showImage()
    global deviceID

    if(enableADB): #this is only here for debugging
        doCommNoCheck('adb wait-for-device')
        print(doCommNoCheck('adb devices'))
        updateDeviceID()
        print(deviceID)
        clearDispContents()
        outText("Found Device", 0, font1)
        outText(deviceID, 1, font1)
        showImage()

#We use aapt here just to get the app name and display it on the OLED. It's fast enough for me not to care about slowing things down..
def installApp(app):
    clearDispContents()
    print ("\n ADB Installing: " + app)
    command = "aapt dump badging {} | grep \"application: label\"".format(app)
    output = os.popen(command).readline().replace("application: label='", "")
    output = output.split("'")[0]
    print ("Output:", output)
    name = output
    outText("Installing........", 0, font1)
    outText(name, 1, font2)
    showImage()
    command = "adb install -r {}".format(app)
    output = doComm(command)

    output = "Success"
    time.sleep(1)
    return output

#outputs text to the 2nd line on the oled.
def outLine(text):
    clearDispContents()
    outText(text, 1, font1)
    showImage()

    
#I hate this so much...It takes forever, and is the worst during the amazon setup screen, as adb is SLOW
def getUI():
    print (doComm("adb shell uiautomator dump"))
    return doComm("adb shell cat /sdcard/window_dump.xml")


#Dumpsys is typically fast enough not to care here. 
def getCurrentFocus():
    focus = doComm("adb shell dumpsys window windows | grep -E mCurrentFocus")
    print (focus)
    return focus


#Annoying, but needs to be done. 
#When you first connect to WiFi, your time zone is updated. A notification popup is displayed, which can interupt the current process 
#   and cause us to be a tap behind.
def checkTimeZone():
    if ("com.amazon.kindleautomatictimezone.receiver.AtzUserPreferenceDialogActivity" in getCurrentFocus()):
        doComm("adb shell input tap 215 575")
        print ("Done time zone check....")
        return True
    return False
            #time.sleep(1)
    #doComm("adb shell input tap 215 575")
    #print("Completed time check")
    #outLine("Time Check Done")

    
    

def disableAds():
    clearDispContents()
    outText("Clear Lockscreen", 0, font1)
    outText("Advertisements...", 1, font1)
    showImage()
    if (enableADB):
        #This unfortunately doesnt seem to work. They keep coming back :(
        print(doComm("adb shell settings put global LOCKSCREEN_AD_ENABLED 0")) # && pm clear com.amazon.kindle.kso"))

        
#not necessary, but it helps. This is one of the first things I do when I get a new phone. 
#The time out is not necessary. I used it mainly for debug, but decided to keep it when setting up final devices.
def screenStuff():
    clearDispContents()
    outText("Clearing Animator", 0, font1)
    outText("Transition Scale", 1, font1)
    showImage()
    doComm("adb shell settings put global animator_duration_scale 0.0 && "
           + "settings put global transition_animation_scale 0.0 && "
           + "settings put global window_animation_scale 0.0 && "
           + "settings put system screen_off_timeout 300000")
    clearDispContents()
    global screenDone
    screenDone=True
    
    
    
#For whatever reason, this needs to be done in a particular order.
#Otherwise, it could have been kept in the folder with the other apps.

def installPlay():
    installApp("/home/pi/googlePlay/com.google.android.gsf.login.apk")
    installApp("/home/pi/googlePlay/com.google.android.gsf.apk")
    installApp("/home/pi/googlePlay/com.google.android.gms.apk")
    installApp("/home/pi/googlePlay/com.android.vending.apk")


#Change the filepath to what you'd like. 
def installApps():
    success = 0
    fail = 0
    total = 0
    print("Installing Apps....")
    print(os.listdir("/home/pi/"))
    for i in os.listdir("/home/pi/"):
        if isfile(i) and i.endswith("apk"):
            if("Success" in installApp(i)):
                success = success + 1
            else:
                fail = fail + 1
            total = total + 1
    print("Success: " + str(success))
    print("Fail: " + str(fail))
    print("Total: " + str(total))
    clearDispContents()
    outText("Installs Done!", 0, font1)
    outText("Success {} / {}".format(success, total), 1, font2)
    time.sleep(1)

    global appsInstalled
    appsInstalled = True



#Set passcode to what you want. Many places prefer something simple, like 1111 or 1234.
def setPasscode():
    global passCodeSet
    clearDispContents()
    outText("SetPasscode:1234", 0,font1)
    outText("DO NOT TOUCH!!!!", 1, font1)
    showImage()
    doComm("adb shell am start -a android.settings.SECURITY_SETTINGS")
    doComm("adb shell input tap 300 180 && input text 1234")
    doComm("adb shell input keyevent 61 && input text 1234 && input tap 170 430")
    passCodeSet=True

    
#There are better ways of doing this, and needs some updating. It works within my preference for now though. 
#Occasionally, it seemed to touch an already connected AP, but once it realizes it has an IP that doesn't really matter. 
#I'll be fixing this in the future.  
#The reason I opted to upload a bash script to the device though, is because of all the extra time it would take 
#   to communicate via ADB. Doing it through an uploaded script was a few seconds faster when the AP
#   wasn't the first few in the list. 
def connectWifi(SSID, passphrase):
    clearDispContents()
    outText("Wifi Connect.", 0, font1)
    outText("Do Not Touch!", 1, font1)
    showImage()
    global connected
    doComm("adb push /home/pi/wifi.sh /sdcard/wifiConnect.sh")

    wifiOutput = ""
    ip=""
    while("192.168.0" not in wifiOutput):
        doComm("adb shell sh /sdcard/wifiConnect.sh {} {}".format(SSID, passphrase))
        print("Waiting for IP..")
        time.sleep(10)
        wifiOutput = doComm("adb shell ifconfig wlan0").splitlines()[1].strip()#.split(" ")[1]
        print(wifiOutput)
        ip = re.split(",| |:", wifiOutput)[2]
        if ("com.android.settings.SubSettings" in getCurrentFocus()):
            doComm("adb shell input keyevent 4")

    print ("IP: ", ip)
    clearDispContents()
    outText("Detected IP:", 0, font1)
    outText(ip, 1, font1)
    showImage()
    connected=True
    time.sleep(1)
    clearDispContents()

    
    
#Alright, I know things got messy with if statements..... Things will be fixed in the future when I have time. 

def doChrome(focus):
    global chromeDone    
    #Open with chrome or silk?
    
    
    while ("Application Not Responding" in getCurrentFocus()):
        doComm("adb shell input tap 300 500")
        
    if("com.android.internal.app.ResolverActivity" in focus):
        print ("Choose Chrome")
        doComm("adb shell input tap 180 800 && input tap 500 940")
        #focus = getCurrentFocus()
    
    #Welcome to chrome!
    focus = getCurrentFocus()
    if ("org.chromium.chrome.browser.firstrun.FirstRunActivity" in focus):
        outLine("WelcomeToChrome!")
        ui = getUI()
        if ("Help make Chrome better by" in ui):
            print("Done waiting for Welcome page..")    
            print ("Uncheck usage reports")
            #Don't send usage reports, accept & Continue
            doComm("adb shell input tap 110 600 && input tap 300 750")
        if ("Turn on sync" in ui):
            print("No Thanks to accounts..")
            doComm("adb shell input tap 100 750 && input keyevent 3")
            chromeDone = True
    if ("org.chromium.chrome.browser.ChromeTabbedActivity" in focus):
        chromeDone = True
    
    #Sometimes it crashed during debug. 
    if ("chrome" not in focus and not chromeDone):
        print(doComm("adb shell am start -a android.intent.action.VIEW -d http://tabs4covid.com"))

    
def amazonSignIn():
    focus=getCurrentFocus()
    global accountsDone
    
    if ("Application Not Responding" in focus):
        doComm("adb shell input tap 300 500")
        
    while ("com.amazon.oobe.registration.RegistrationActivity" in getCurrentFocus()):
        time.sleep(2)
        #Enter Credentials
        doComm("adb shell input text {}".format(AMAZON_EMAIL) + " && input tap 70 410 && input keyevent 66 && input tap 100 350")
        #doComm("adb shell input tap 100 350")
        doComm("adb shell input text {}".format(AMAZON_PASS) + " && input tap 300 550 && input tap 470 945")
        #Finish
        focus = getCurrentFocus()
        for i in range(15):
            clearDispContents()
            outText("Sleeping for", 0, font1)
            outText(str(15-i) + " more seconds", 1, font1)
            showImage()
            time.sleep(1)

    clearDispContents()
    outText("Warning: ADB is", 0, font1)
    outText("SUPER slow here.", 1, font1)
    showImage()
    #unfortunately, we need to wait a second here too. But i thankfully was able to get this to work without ui automator
    if ("com.amazon.kindle.otter.oobe.modules.amazonServices.FireOptionsActivity" in focus or "com.amazon.kindle.otter.oobe.modules.amazonServices.FireOptions.View.FireOptionsActivity" in focus):
        print("uncheck stuff....")
        doComm("adb shell input tap  70 155 && input tap  70 285 && input tap  70 445")
        
        print ("Press Okay")
        doComm("adb shell input tap 480 960")
    
    if ("com.amazon.kindle.otter.oobe.modules.firstRunVideo.VideoActivity" in getCurrentFocus()):
        outLine("Skip video...")
        print ("try skip the video, but wait for it to come up")
        time.sleep(2)
        
        while ("com.amazon.kindle.otter.oobe.modules.firstRunVideo.VideoActivity" in getCurrentFocus()):
            doComm("adb shell input tap 540 890 && input tap 540 890 && input tap 540 890")
            outLine("Not kids Account")
    
    if ("com.amazon.kindle.otter.oobe.modules.household.views.KidFriendlyActivity" in getCurrentFocus()):
        doComm("adb shell input tap  75 680 && input tap 480 960")
        accountsDone = True
        
    if ("com.amazon.kindle.otter.oobe.modules.upsell.controller.UpsellActivity" in getCurrentFocus()):
        doComm("adb shell input tap 470 960")
    if ("com.amazon.firelauncher.Launcher" in getCurrentFocus()):
        ui = getUI()
        if ("You now have access to" in ui):
            doComm("adb shell input tap 565 40")
        if ("text=\"Learn more about Alexa" in ui):
            doComm("adb shell input tap 300 915")
        if ("Amazon processes and retains audio" in ui):
            doComm("adb shell input tap 125 915")
        if ("If you exit now" in ui):
            doComm("adb shell input tap 480 915")
            
            accountsDone = True
         
        
#Not totally necessary to have done it this way, but it was mostly for debugging.... 
def performOnCurrentFocus():
    global chromeDone
    global accountsDone

    focus=getCurrentFocus()

    #should be first thing after wifi intent.
    #This is the "Confirm Time Zone" Dialog
    if ("com.amazon.kindleautomatictimezone.receiver.AtzUserPreferenceDialogActivity" in focus):
        doComm("adb shell input tap 215 575")
        print ("Time zone check finished.")
    
    if (not chromeDone):
        doChrome(focus)
        
    if (chromeDone and not accountsDone):
        amazonSignIn()
        
    #if ("com.amazon.kindle.otter.oobe.modules" in getCurrentFocus()):
        #accountsDone=False
        #amazonSignIn()
        


#Not used right now. I disconnected manually during QC when I made sure Alexa is turned off.
def disconnectWifi():
    global forgotten
    print("Disconnecting....")
    outLine("Disconnecting...")
    doComm("adb shell am start -a android.settings.WIFI_SETTINGS")
    if ("com.android.settings.SubSettings" in getUI()):
        doComm("adb shell input tap 300 225 && input tap 125 280")
        forgotten=True
        
        
#Mainly did this for debugging. At this point, everything's a mess.....
#I did this in a sleep deprived state when I was having trouble making sure a device didn't go through setup more than once.
#If you include a device ID, the first tablet should not have anything done to it, while the next will. 
#If you don't include it, everything gets set to false anyway..
screenDone=True
passCodeSet=True
appsInstalled=True
connected=True

chromeDone = True
accountsDone=True
forgotten=True

#checkDevice()
doneDevices = []
#doneDevices.append("")
#deviceID=""
while (True):
    
    # this is a redundency check.
    # It'll probably still be fine with the millionth while loop we have at the bottom
        
    if (deviceID != getDeviceID()):
        old = deviceID
        checkDevice()
        print("Old ID:" + old)
        print("New ID:" + deviceID)
       
        screenDone=False
        passCodeSet=False
        appsInstalled=False
        connected=False
        chromeDone = False
        
        accountsDone=False
        forgotten=False

        #yes, I know getDeviceID is being ran multiple times here..
    
        
    if(not screenDone):
        screenStuff()
        
    if(not passCodeSet):
        setPasscode()
        
    if(not appsInstalled):
        installPlay()
        installApps()
        
    if (not connected):
        connectWifi(WIFI_SSID, WIFI_PASS)
        clearDispContents()
        outText("Navigating to", 0, font1)
        outText("tabs4covid.com", 1, font2)
        showImage()
        print(doComm("adb shell am start -a android.intent.action.VIEW -d http://tabs4covid.com"))


    while (not accountsDone):
        time.sleep(2)
        if (chromeDone and not accountsDone and "com.amazon.kindle.otter.oobe" not in getCurrentFocus()):
            print ("Start account activity")
            outLine("Sign In Amazon")
            doComm("adb shell am start -a com.amazon.kindle.otter.oobe.LAUNCH_BY_MYACCOUNT")
        
        performOnCurrentFocus()

    clearDispContents()
    
    #I run this regardless because of how often they come back. Seems like amazon has multiple checks in place
    if(disableAd):
        disableAds()
        
    #outText("Done!", 0, font1)
    #showImage()
    
    #while (not forgotten): 
    #    disconnectWifi()
    
    if(accountsDone and chromeDone and appsInstalled and passCodeSet and screenDone):
        outLine("Done!")
        time.sleep(4)
        doComm("adb reboot")
        #updateDeviceID()
        doneDevices.append(deviceID)
        while ("error" in getDeviceID() or deviceID == getDeviceID()):
            time.sleep(2.5)
            #I put this inside the loop so I can pay attention to the flash
            clearDispContents()
            print("waiting for next device....")
            outText("Waiting for next", 0, font1)
            outText("device", 1, font1)
            showImage()
#oled.image(image)
#oled.show()

