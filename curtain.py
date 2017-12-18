import spidev
import RPi.GPIO as gpio
from time import *
import sys
import pygame

pygame.init()

spi = spidev.SpiDev()
spi.open(0,0)

gpio.setmode(gpio.BCM)

motorpin1 = 19
motorpin2 = 26

gpio.setup(motorpin1, gpio.OUT)
gpio.setup(motorpin2, gpio.OUT)

curtain_up = True

def analog_read(channel):
    r = spi.xfer2([1, (8+channel) << 4, 0])
    adc_out = ((r[1]&3) << 8) + r[2]
    return adc_out

light = analog_read(0)
voltage = light * 3.3/1024
auto_mode = True

screen = pygame.display.set_mode([400,400])

while True:
    light = analog_read(0)
    try:
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP and curtain_up == False:
                    gpio.output(motorpin1, False)
                    gpio.output(motorpin2, True)
                    auto_mode = False
                    curtain_up = True
                    sleep(1.5)
                    gpio.output(motorpin1, False)
                    gpio.output(motorpin2, False)
                elif ev.key == pygame.K_DOWN and curtain_up == True:
                    gpio.output(motorpin1, True)
                    gpio.output(motorpin2, False)
                    auto_mode = False
                    curtain_up = False
                    sleep(1.5)
                    gpio.output(motorpin1, False)
                    gpio.output(motorpin2, False)
                elif ev.key == pygame.K_a:
                    auto_mode = True
        if auto_mode:
           
            if light > 200 and curtain_up:
                gpio.output(motorpin1, True)
                gpio.output(motorpin2, False)
                sleep(1.5)
                curtain_up = False
            elif light < 200 and not curtain_up:
                gpio.output(motorpin1, False)
                gpio.output(motorpin2, True)
                sleep(1.5)
                curtain_up = True
            else:
                gpio.output(motorpin1, False)
                gpio.output(motorpin2, False)
    except KeyboardInterrupt:
        gpio.cleanup()
        sys.exit()
