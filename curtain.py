'''
라즈베리 파이로 아날로그 센서값 받기
코드 참조
http://blog.naver.com/PostView.nhn?blogId=roboholic84&logNo=220367321777&parentCategoryNo=112&categoryNo=&viewDate=&isShowPopularPosts=false&from=section
'''

import spidev               #아날로그 센서값을 받기 위한 SPI통신 모듈
import RPi.GPIO as gpio     #라즈베리 파이 GPIO 모듈
from time import *          #DC 모터의 시간제어용 모듈
import sys                  #프로그램이 끝나면 종료시키기 위한 모듈
import pygame               #키입력을 위한 모듈

pygame.init()               #pygame 패키지를 이용하기 위해 초기화 해준다

spi = spidev.SpiDev()
spi.open(0,0)

gpio.setmode(gpio.BCM)

motorpin1 = 19
motorpin2 = 26

gpio.setup(motorpin1, gpio.OUT)
gpio.setup(motorpin2, gpio.OUT)

'''
curtain_up은 커튼의 현재 상태를 저장한다
만약 커튼이 올라가있는 상황이면
True를 저장하고, 
내려와있는 상태라면
False를 저장한다.
'''
curtain_up = True

def analog_read(channel):
    '''

    :param channel: ADC칩의 n번째 채널을 인자로 가짐
    :return: 디지털 변환된 값을 반환
    '''
    r = spi.xfer2([1, (8+channel) << 4, 0])
    adc_out = ((r[1]&3) << 8) + r[2]
    return adc_out

light = analog_read(0)
voltage = light * 3.3/1024      #조도센서의 값을 전압의 크기로 변환
'''
키입력이 있는 경우 auto_mode는 거짓이 되어 
조도센서의 값에 상관없이 커튼의 상태를 유지시킨다.
'''
auto_mode = True

'''
pygame 패키지의 키입력을 사용하고자 한다면
CLI Window 가 아닌 pygame내장 스크린에서
입력ㄷ해야 함으로 screen을 직접 정의해준다
크기는 가로 : 400 픽셀
       세로 : 400 픽셀
'''
screen = pygame.display.set_mode([400,400])

while True:
    '''
    프로그램이 돌아가는 도중 항상 조도센서의 값을 받아준다.
    또한 키입력이 있는지 확인하고
    키입력이 있는 경우 커튼의 상태와
    A.C.의 모드 등을 변경시켜 준다.
    '''
    light = analog_read(0)      #조도 센서의 값을 받아준다
    try:
        for ev in pygame.event.get():       #pygame의 이벤트 중에서
            if ev.type == pygame.KEYDOWN:   #키보드의 키가 눌렸을 때
                if ev.key == pygame.K_UP and curtain_up == False:   #그 키가 위 방향키고, 커튼이 내려가 있다면
                    gpio.output(motorpin1, False)           #커튼을 올리고
                    gpio.output(motorpin2, True)
                    auto_mode = False       #모드를 Auto에서 변경시키며
                    curtain_up = True       #커튼의 상태를 저장해준다(올라간 상태)
                    sleep(1.5)              #DC 모터를 1.5초간 돌림
                    gpio.output(motorpin1, False)
                    gpio.output(motorpin2, False)
                elif ev.key == pygame.K_DOWN and curtain_up == True:    # 키가 아래 방향키고 커튼이 올라가 있다면
                    gpio.output(motorpin1, True)        #커튼을 내리고
                    gpio.output(motorpin2, False)
                    auto_mode = False       #모드를 Auto에서 변경시키며
                    curtain_up = False      #커튼의 현재 상태를 저장한다.(내려간 상태)
                    sleep(1.5)              #DC 모터를 1.5초간 돌림
                    gpio.output(motorpin1, False)
                    gpio.output(motorpin2, False)
                elif ev.key == pygame.K_a:  #키가 a 키라면
                    auto_mode = True        #Auto모드로 되돌려 준다
        if auto_mode:       #아래 코드는 Auto모드가 아니면 실행되지 않는다

            if light > 200 and curtain_up:  #빛의 크기가 200이상이고 커튼이 올라가 있다면
                gpio.output(motorpin1, True)#커튼을 내리고
                gpio.output(motorpin2, False)
                sleep(1.5)
                curtain_up = False      #커튼의 상태를 내려간 상태로 저장한다
            elif light < 200 and not curtain_up:#빛의 크기가 200이하로 내려가고 커튼이 내려가 있다면
                gpio.output(motorpin1, False)#커튼을 올리고
                gpio.output(motorpin2, True)
                sleep(1.5)
                curtain_up = True           #커튼의 상태를 올라간 상태로 저장한다
            else:
                '''
                혹시 모를 경우를 대비해
                소자를 보호하고자 위의 두가지 상황이 아닌
                오류가 발생 하더라도
                모터를 구동시키지 않음으로서 소자와 보드를 보호한다.
                '''
                gpio.output(motorpin1, False)
                gpio.output(motorpin2, False)
    except KeyboardInterrupt:
        '''
        기본적으로 프로그램이 종료될 일이 없으나
        만약 종료해야될 일이 생긴다면
        Ctrl + C 키를 누르면 프로그램이 종료된다.
        '''
        gpio.cleanup()
        sys.exit()
