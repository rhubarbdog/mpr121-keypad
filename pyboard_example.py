# gnd rq 3.3v sda scl
import pyb
import pyboard_keypad as keypad
import time

i2c = pyb.I2C(2, pyb.I2C.MASTER)
switch = pyb.Switch()

keypad = keypad.KEYPAD(i2c, 'Y12')
ALL_KEYS = [ j+1 for j in range(9) ] + ['*', 0, '#']

while not switch.value():

    if keypad.keypad.is_near():
        print("P", end = ' ')
    else:
        print("-", end = ' ')
                
    for i in ALL_KEYS:
        if keypad.key[i].is_pressed():
            print(str(keypad.key[i]), end = ' ')
        else:
            print('.', end = ' ')

    print('', end = '\r')
                    
    time.sleep_ms(10)


print("")

for i in ALL_KEYS:
    print(i,keypad.key[i].get_presses(),
          keypad.key[i].was_pressed(),
          keypad.key[i].get_presses(),
          keypad.key[i].was_pressed())
