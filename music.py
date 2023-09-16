# import required module
import pygame
import sys
from datetime import datetime

musicDuration = int(sys.argv[1])                # In minutes

pygame.mixer.init()
pygame.mixer.music.load("/home/pi/Music/sonata_22.mp3")
pygame.mixer.music.play()

startTime = datetime.now()

print("Playing music for " + str(musicDuration) + " minute(s)")

while pygame.mixer.music.get_busy() == True:
    currentTime = datetime.now()
    seconds = currentTime - startTime
    minutes = seconds.total_seconds() / 60
    if minutes >= musicDuration:
        exit(0)
    continue

exit(0)