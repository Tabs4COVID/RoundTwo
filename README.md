# RoundTwo
Code used during the second wave of tablet donations. There are a few bugs, but it works enough to be usable.

# Notes: 
- We often use `adb shell input tap X_COORD Y_COORD` to control where to touch. Startup.py was made for Fire 7 9th Gen, model: M8S26G. If you have a different model or screen, your tap locations might be different. Confirm this before proceeding. If you need to find out cursor location, you can use developer options > show pointer location to show your touch coordinates. 
- In the top of the `startup.py` file, there are constants with login info. You'll need to modify that. Additionally, the lockscreen code is set as 1234. You'll have to modify that in the function if you want to to be something else.
- Remember to include `startup.py` in your .bashrc file. 
- This was (mistakenly) set up in `/home/pi/`. That's not terrible, being that it's a designated device, but you'll have to put all the APKs that you'll be installing in the same folder; same with `wifi.sh`. Google services/play store goes into its own folder, in `/home/pi/googlePlay`. Just modify the filepaths if you want it elsewhere. 
-make sure to install pip3, adafruit-circuitpython-ssd1306, python-board, and python3-smbus for the oled. 
-Additionally, don't forget to enable I2C in rasbpi-config.

that should be it for now, but I'm open to questions. I'll modify if I realize I forgot anything..




# ToDo
- Fix Filepaths so we're not in /home/pi. 
- Fix WifiConnect. We really don't need to have it sleep, but I was lazy. This turned out much bigger than I had planned. 
- Find a better way than `doComm` ("do command") and `doCommNoCheck`. I feel like this should have a simple solution, but I've got a block.
- I HATE calling the uiautomator. It's not terrible that I'm "cheating" the way it gets parsed, but calling it takes FOREVER. 
- Find a more effective way to confirm `chromeDone` and `accountsDone`. There's quite a bit that can be looked at in `adb shell settings list GLOBAL` that I haven't gotten to paying close attention to yet.
- seperate `accountsDone` into `accountsDone` and `tutorialDone`
- Fix the bugginess between screens. 
- Create a method to include the option to have a different sign in account for each tablet. email1@domain.com, email2@domain.com.. This must be stored in a temp file in case we have to reboot.
- There's a bit more I can't remember at the moment..
