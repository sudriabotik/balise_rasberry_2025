#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#alex
from RPLCD.i2c import CharLCD
from time import sleep
a=0
while a!=10:
    lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
    lcd.clear()
    lcd.write_string("sudriabotik")
    sleep(50 )
    
    lcd.clear()
    print("tas position" ,a)
    a+=1
