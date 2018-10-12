import RPi.GPIO as GPIO
import raspberry_keypad as keypad
import time

GPIO.setmode(GPIO.BCM)

keypad = keypad.KEYPAD(1, 23)
ALL_KEYS = [ j+1 for j in range(9) ] + ['*', 0, '#']

try:
    while True:

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
                    
        time.sleep(0.01)

except KeyboardInterrupt:
    pass

print("")
GPIO.cleanup()

for i in ALL_KEYS:
    print(i,keypad.key[i].get_presses(),
          keypad.key[i].was_pressed(),
          keypad.key[i].get_presses(),
          keypad.key[i].was_pressed())
