#!/bin/bash

adb shell pm list packages -a -f | cut -d: -f2 | awk -F'=' '{gsub(" ", ""); print $1" "$2".apk" }' | xargs -r -n2 -t adb pull
