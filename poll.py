import subprocess
import memcache
from datetime import datetime
import time

# Prepare memcache for storing start time
memc = memcache.Client(['127.0.0.1'], debug=1)

pollSeconds = 15
withinSeconds = 30

print(str(datetime.now()) + " poll.py started")

while True:

    now = datetime.now()
    
    startDateTime = memc.get("mem_light_start_date_time")

    if startDateTime != None and startDateTime != 0:
        if startDateTime >= now:
            seconds = abs((startDateTime-now).total_seconds())
            lightDurationMins = memc.get("mem_light_duration")
            if seconds <= withinSeconds and lightDurationMins > 0:
                print(str(datetime.now()) + " Running light.py since startDateTime is within " + str(withinSeconds) + " seconds: " + str(startDateTime))
                # Clear out the memcache start time so that we do not accidentally start it again
                memc.set("mem_light_start_date_time", 0)
                memc.set("mem_light_duration", 0)

                # Run the light and music scripts
                l = subprocess.Popen(['python', 'light.py', str(lightDurationMins)])
                m = subprocess.Popen(['python', 'music.py', str(lightDurationMins)])

                #subprocess.run(["python", "light.py", str(lightDurationMins), ">> /tmp/light.log"])
                #subprocess.run(["python", "music.py", str(lightDurationMins), ">> /tmp/music.log"])
                #subprocess.run(["python", "light.py", str(lightDurationMins), '&'])
                #subprocess.run(["python", "music.py", str(lightDurationMins), '&'])
        else:
            print(str(datetime.now()) + " Nothing to do since startDateTime is in the past: " + str(startDateTime))
    else:
        print(str(datetime.now()) + " Nothing to do due to invalid startDateTime: " + str(startDateTime))

    time.sleep(pollSeconds)              # Wait before checking again


