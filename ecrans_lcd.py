#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from RPLCD.i2c import CharLCD

def setup_lcd():

    lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
    lcd.clear()
    lcd.write_string("setup done!")
    return lcd

def message_lcd(lcd, text):
    lcd.clear()
    lcd.write_string(text)
    return None