from time import sleep
from machine import I2C, Pin 
from i2c_lcd import I2cLcd 

AddressOfLcd = 0x27
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000) # connect scl to GPIO 22, sda to GPIO 21
lcd = I2cLcd(i2c, AddressOfLcd, 2, 16)

# code in ra màn hình lcd
lcd.move_to(3,0) #đưa con trở đến cột 3 hàng 0
lcd.putstr('Micropython') #in chữ 'Micropython'

lcd.move_to(0,1) #đưa con trở đến cột 0 hàng 0
lcd.putstr("hello fschooler")