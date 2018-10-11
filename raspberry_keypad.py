import RPi.GPIO as GPIO
import posix
from fcntl import ioctl

IOCTL_I2C_SLAVE = 0x0703

class KEY:

    def __init__(self, symbol):
        self._symbol = symbol
        self._is_pressed = False
        self._was_pressed = False
        self._get_presses = 0

    def __str__(self):
        return self._symbol

    def is_pressed(self):
        return self._is_pressed

    def was_pressed(self):
        save = self._was_pressed
        self._was_pressed = False
        return save

    def get_presses(self):
        save = self._get_presses
        self._get_presses = 0
        return save

    def _touch(self):
        self._is_pressed = True
        self._was_pressed = True
        self._get_presses += 1

    def _release(self):
        self._is_pressed = False


class PROXIMITY:

    def __init__(self):
        self._is_near = False
        self._was_near = False

    def is_near(self):
        return self._is_near

    def was_near(self):
        save = self._was_near
        self._was_near = False
        return save

    def _close_by(self):
        self._is_near = True
        self._was_near = True

    def _far_away(self):
        self._is_near = False


class KEYPAD:

    def __init__(self, i2c, rq_pin, address = 0x5a):
        self._fd = posix.open('/dev/i2c-%d' % i2c, posix.O_RDWR)
        ioctl(self._fd, IOCTL_I2C_SLAVE, address)

        self._rq_pin=rq_pin
        GPIO.setup(self._rq_pin, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(self._rq_pin, GPIO.FALLING,
                              callback=self._read_keys)

        self._pads = ( KEY('1'), KEY('4'), KEY('7'), KEY('*'),
                       KEY('2'), KEY('5'), KEY('8'), KEY('0'),
                       KEY('3'), KEY('6'), KEY('9'), KEY('#') )
        self.keypad = PROXIMITY() 
        self.key = { 1 : self._pads[0],
                     2 : self._pads[4],
                     3 : self._pads[8],
                     4 : self._pads[1],
                     5 : self._pads[5],
                     6 : self._pads[9],
                     7 : self._pads[2],
                     8 : self._pads[6],
                     9 : self._pads[10],
                     0 : self._pads[7],
                     '1' : self._pads[0],
                     '2' : self._pads[4],
                     '3' : self._pads[8],
                     '4' : self._pads[1],
                     '5' : self._pads[5],
                     '6' : self._pads[9],
                     '7' : self._pads[2],
                     '8' : self._pads[6],
                     '9' : self._pads[10],
                     '0' : self._pads[7],
                     '*' : self._pads[3],
                     '#' : self._pads[11] }
        
        self._configure()
        self.switch_on()
        
    def __del__(self):
        posix.close(self._fd)

    def _configure(self):
        self.reset()
        # Touch baseline filter
        # rising, baseline quick rising
        posix.write(self._fd, b'\x2b\x01') # max half delta rising
        posix.write(self._fd, b'\x2c\x01') # noise half delta rising
        posix.write(self._fd, b'\x2d\x00') # noise count limit rising
        posix.write(self._fd, b'\x2e\x00') # delay limit rising
        #falling, baseline slow falling
        posix.write(self._fd, b'\x2f\x01') # max half delta falling
        posix.write(self._fd, b'\x30\x01') # noise delta falling
        posix.write(self._fd, b'\x31\xff') # noise count limit falling
        posix.write(self._fd, b'\x32\x00') # delay limit falling
        #touched, baseline keep
        posix.write(self._fd, b'\x33\x00') # noise half delta touched
        posix.write(self._fd, b'\x34\x00') # noise count touched
        posix.write(self._fd, b'\x35\x00') # delta limit touched
        #proximity baseline filter
        # rising, very quick rising
        posix.write(self._fd, b'\x36\x0f') # max half delta rising
        posix.write(self._fd, b'\x37\x0f') # noise half delta rising
        posix.write(self._fd, b'\x38\x00') # noise count limit rising
        posix.write(self._fd, b'\x39\x00') # delay limit rising
        #falling, very slow rising
        posix.write(self._fd, b'\x3a\x01') # max half delta falling
        posix.write(self._fd, b'\x3b\x01') # noise delta falling
        posix.write(self._fd, b'\x3c\xff') # noise count limit falling
        posix.write(self._fd, b'\x3d\xff') # delay limit falling
        #touched
        posix.write(self._fd, b'\x3e\x00')
        posix.write(self._fd, b'\x3f\x00')
        posix.write(self._fd, b'\x40\x00')
        # touchpad threshold
        address = 0x40
        data = bytearray(2)
        for i in range(12):
            for datum in (10, 8): #touch/release
                address += 1
                data[0] = address
                data[1] = datum
                posix.write(self._fd, data)

        posix.write(self._fd, b'\x059\x06') # proximity Touch
        posix.write(self._fd, b'\x05a\x04') # proximity Release
        #touce/release interupt debounce
        posix.write(self._fd, b'\x058\x00')
        #AFE and filter config
        posix.write(self._fd, b'\x05c\x10')
        posix.write(self._fd, b'\x05d\x24')
        posix.write(self._fd, b'\x05e\x80')
        # Auto config
        posix.write(self._fd, b'\x07b\x0B')
        posix.write(self._fd, b'\x07c\x80')
        posix.write(self._fd, b'\x07d\xc8')
        posix.write(self._fd, b'\x07e\x82')
        posix.write(self._fd, b'\x07f\xb4')
        
    def reset(self):
        posix.write(self._fd, b'\x80\x63')
        
    def switch_on(self):
        posix.write(self._fd, b'\x5e\xbc')

    def _read_keys(self, pin):
        posix.write(self._fd, b'\x00')
        keys = bytearray(posix.read(self._fd,2))
        keycode = (keys[1] & 0x1f) << 8 | keys[0]

        # keys 0 to 9 and # & *
        for i in range(12):
            mask = 0x01 << i

            if mask & keycode:
                self._pads[i]._touch()
            else:
                self._pads[i]._release()

        # proximity
        mask = 0x01 << 12

        if mask & keycode:
            self.keypad._close_by()
        else:
            self.keypad._far_away()
