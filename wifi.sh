#/bin/bash

echo "Open Wifi Settings.."
am start -a android.settings.WIFI_SETTINGS
wifi=$1
pass=$2
#tapY=210
#i=1
tapY=145
#input tap 400 $tapY
echo "Dump UI XML...."
#uiautomator dump

xml="" #$(cat /sdcard/window_dump.xml)

while [[ $xml != *"text=\""${wifi}"\""* ]]; do
	echo "here"
	input tap 300 90
	#((i++))
	tapY=$(($tapY + 65 ))
	input tap 300 $tapY
	echo "Tapping at 300, $tapY"
	uiautomator dump
	xml=$(cat /sdcard/window_dump.xml)

	#If we hit the "Add Network" button at the bottom, 
	#	wait 5 seconds and start over at 210
	if [[ $xml == *"text=\"Enter the SSID\""* ]]; then
		tapY=210
		sleep 5
		echo "Starting back at 210.."
	fi
	#if we're at the input password screen...
	if [[ $xml == *"com.android.settings:id/show_password"* ]]; then
		#if correct wifi...
		if [[ $xml == *$wifi* ]]; then
			echo "Found $wifi"
			input text "$pass"
			input keyevent 66
			break
		fi
	fi
done


