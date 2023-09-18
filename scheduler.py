import PySimpleGUI as sg
import memcache
from datetime import datetime, timedelta
import time
import subprocess
import os

def main():

    global memc

    # Prepare memcache for storing start time
    memc = memcache.Client(['127.0.0.1'], debug=1)

    # Get the stored settings from memory
    prevBeginHours = memc.get("mem_light_prev_begin_in_hours")
    if prevBeginHours == None:
        prevBeginHours = 0
    
    prevStartHour = memc.get("mem_light_prev_starting_hour")
    if prevStartHour == None:
        prevStartHour = 1
    prevStartMin = memc.get("mem_light_prev_starting_min")
    if prevStartMin == None:
        prevStartMin = 0
    prevStartampm = memc.get("mem_light_prev_starting_ampm")
    if prevStartampm == None:
        prevStartampm = 'AM'
    
    prevDuration = memc.get("mem_light_prev_duration")
    if prevDuration == None:
        prevDuration = 5
    
    print(get_schedule(beginInHours=prevBeginHours, startingHour=prevStartHour, startingMin=prevStartMin, startingampm=prevStartampm, lightDuration=prevDuration, font='_ 15'))

def calculateStartDateTime(inHours, startHour, startMin, ampm):

    now = datetime.now()

    if inHours > 0:
        myDate = datetime.now() + timedelta(hours=inHours)

    elif startHour > 0:
        if ampm == 'PM':
            startHour += 12                      # We will use 24 hour time so add 12 if it's a PM selection

        dt = now
        myDate = dt.replace(hour=startHour, minute=startMin)              # Replace the current time with the schedule hour and minute
        if myDate < now:
            myDate = myDate + timedelta(days=1)

    else:
        myDate = None

    return myDate


def get_schedule(title='Circadian Light Schedule', beginInHours=None, startingHour=None, startingMin=None, startingampm=None, lightDuration=None, allowManualInput=True, font=None):

    maxValueDict = {'-STARTINGHOUR-':(1, 12), '-STARTINGMIN-':(0, 59)}
    hourList = [i for i in range(0, 15)]
    minuteList = [i for i in range(-1, 62)]

    infoMessage = sg.Text('', visible=True, text_color='White', font='Helvetica 40')

    column_to_be_centered = [
             [sg.Text(title, font=('Helvetica 90'))],
             [sg.Text('')],
             [sg.Text('Begin in'),
              sg.Combo(['0', '1', '2', '3', '4'], beginInHours, key='-BEGININHOURS-', enable_events=True, readonly=True),
              sg.Text('hour(s) or at'),
              sg.Spin(hourList, initial_value=startingHour, key='-STARTINGHOUR-', s=3, enable_events=True, readonly=not allowManualInput),
              sg.Text(':'),
              sg.Spin(minuteList, initial_value=startingMin, key='-STARTINGMIN-', s=3, enable_events=True, readonly=not allowManualInput),
              sg.Combo(['AM', 'PM'], startingampm, readonly=True, key='-AMPM-')],
             [sg.Text('')],
             [sg.Text('for a duration of'),
              sg.Combo(['1', '5', '10', '15', '30', '45', '60'], lightDuration, key='-LIGHTDURATION-', readonly=not allowManualInput),
              sg.Text('minute(s)')],
             [infoMessage],
             [sg.Button('Start'), sg.Button('Cancel'), sg.Button('Exit')]
            ]

    layout = [[sg.Text(key='-EXPAND-', font='ANY 1', pad=(0, 0))],  # the thing that expands from top
              [sg.Text('', pad=(0,0),key='-EXPAND2-'),              # the thing that expands from left
               sg.Column(column_to_be_centered, vertical_alignment='center', justification='center',  k='-C-')]]

    window = sg.Window(title, layout, no_titlebar=True, font=('Helvetica 70'), location=(0,0), size=(1920,1080), keep_on_top=True, finalize=True)
    #window = sg.Window(title, layout, location=(0,0), size=(1920,1080), keep_on_top=True)

    window['-C-'].expand(True, True, True)
    window['-EXPAND-'].expand(True, True, True)
    window['-EXPAND2-'].expand(True, False, True)

    startingHour = 0
    startingMin =  0
    ampm = ""
    beginInHours = 0
    lightDuration = 0

    while True:
        event, values = window.read()
        # print(event, values)
        if event == sg.WIN_CLOSED or event == 'Cancel':
            startingHour = startingMin = ampm = None
            memc.set("mem_light_start_date_time", 0)
            memc.set("mem_light_duration", 0)
            print("Schedule canceled")
            infoMessage.update('Schedule canceled!')
            infoMessage.update(text_color='Yellow')
            infoMessage.update(visible=True)

            # Run the light and music scripts to stop everything
            l = subprocess.Popen(['python', 'light.py', '0'])
            os.system('pkill -f music.py')

        if event == '-STARTINGHOUR-' or event == '-STARTINGMIN-':
            spin_value = values[event]
            if spin_value > maxValueDict[event][1]:
                values[event] =  maxValueDict[event][0]
                window[event].update(values[event])
            elif spin_value < maxValueDict[event][0]:
                values[event] =  maxValueDict[event][1]
                window[event].update(values[event])

            window['-BEGININHOURS-'].update(set_to_index=0)             # Reset to 0 since a specific time is being selected

        if event == '-BEGININHOURS-':
            window['-STARTINGHOUR-'].update(1)
            window['-STARTINGMIN-'].update(0)
            window['-AMPM-'].update('AM')

        if event == 'Start':
            #print("Starting...")
            # Do validation on the input values to ensure they're valid
            try:
                beginInHours = int(values["-BEGININHOURS-"])

                startingHour = int(values["-STARTINGHOUR-"])
                startingMin =  int(values["-STARTINGMIN-"])
                ampm = values["-AMPM-"]

                lightDuration = int(values["-LIGHTDURATION-"])
                
                # Save the user's choices for next time
                memc.set("mem_light_prev_begin_in_hours", beginInHours)
                memc.set("mem_light_prev_starting_hour", startingHour)
                memc.set("mem_light_prev_starting_min", startingMin)
                memc.set("mem_light_prev_starting_ampm", ampm)
                memc.set("mem_light_prev_duration", lightDuration)

                # Store the schedule selection in a time object in memcache
                memc.set("mem_light_start_date_time", calculateStartDateTime(beginInHours, startingHour, startingMin, ampm))

                # Store the light duration selection in a time object in memcache
                memc.set("mem_light_duration", lightDuration)

            except:
                continue        # if not valid, then don't allow exiting the window using OK.
            if  1 <= startingHour <= 12 and 0 <= startingMin < 60:     # make sure the hour and minute values are in a valid range
                print("Schedule set!")
                infoMessage.update('Schedule set!')
                infoMessage.update(text_color='Yellow')
                infoMessage.update(visible=True)
                print("Turning off screen")
                # Turn off screen
                subprocess.run(["xset", "dpms", "force", "off"])
                #break

        if event == 'Exit':
                break

    window.close()

    print("----")
    print("Current:")
    print("Next start time: " + str(memc.get("mem_light_start_date_time")))
    print("Light duration: " + str(memc.get("mem_light_duration")))

    print(" ")
    
    print("Stored:")
    print("begin_in_hours: " + str(memc.get("mem_light_prev_begin_in_hours")))
    print("starting_hour: " + str(memc.get("mem_light_prev_starting_hour")))
    print("starting_min: " + str(memc.get("mem_light_prev_starting_min")))
    print("starting_ampm: " + memc.get("mem_light_prev_starting_ampm"))
    print("light_duration: " + str(memc.get("mem_light_prev_duration")))
    print("----")

    return beginInHours, startingHour, startingMin, ampm, lightDuration

if __name__ == '__main__':    
    main()
