import pyb

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
        self._i2c = i2c
        self._address = address
        self._buffer = bytearray(2)

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

        pyb.ExtInt(rq_pin, pyb.ExtInt.IRQ_FALLING,
                   pyb.Pin.PULL_UP, self._read_keys)

    def _configure(self):
        self.reset()
        # Touch baseline filter
        # rising, baseline quick rising
        self._i2c.send(b'\x2b\x01', self._address) # max half delta rising
        self._i2c.send(b'\x2c\x01', self._address) # noise half delta rising
        self._i2c.send(b'\x2d\x00', self._address) # noise count limit rising
        self._i2c.send(b'\x2e\x00', self._address) # delay limit rising
        #falling, baseline slow falling
        self._i2c.send(b'\x2f\x01', self._address) # max half delta falling
        self._i2c.send(b'\x30\x01', self._address) # noise delta falling
        self._i2c.send(b'\x31\xff', self._address) # noise count limit falling
        self._i2c.send(b'\x32\x00', self._address) # delay limit falling
        #touched, baseline keep
        self._i2c.send(b'\x33\x00', self._address) # noise half delta touched
        self._i2c.send(b'\x34\x00', self._address) # noise count touched
        self._i2c.send(b'\x35\x00', self._address) # delta limit touched
        #proximity baseline filter
        # rising, very quick rising
        self._i2c.send(b'\x36\x0f', self._address) # max half delta rising
        self._i2c.send(b'\x37\x0f', self._address) # noise half delta rising
        self._i2c.send(b'\x38\x00', self._address) # noise count limit rising
        self._i2c.send(b'\x39\x00', self._address) # delay limit rising
        #falling, very slow rising
        self._i2c.send(b'\x3a\x01', self._address) # max half delta falling
        self._i2c.send(b'\x3b\x01', self._address) # noise delta falling
        self._i2c.send(b'\x3c\xff', self._address) # noise count limit falling
        self._i2c.send(b'\x3d\xff', self._address) # delay limit falling
        #touched
        self._i2c.send(b'\x3e\x00', self._address)
        self._i2c.send(b'\x3f\x00', self._address)
        self._i2c.send(b'\x40\x00', self._address)
        # touchpad threshold
        address = 0x40
        data = bytearray(2)
        for i in range(12):
            for datum in (10, 8): #touch/release
                address += 1
                data[0] = address
                data[1] = datum
                self._i2c.send(data, self._address)

        self._i2c.send(b'\x059\x06', self._address) # proximity Touch
        self._i2c.send(b'\x05a\x04', self._address) # proximity Release
        #touce/release interupt debounce
        self._i2c.send(b'\x058\x00', self._address)
        #AFE and filter config
        self._i2c.send(b'\x05c\x10', self._address)
        self._i2c.send(b'\x05d\x24', self._address)
        self._i2c.send(b'\x05e\x80', self._address)
        # Auto config
        self._i2c.send(b'\x07b\x0B', self._address)
        self._i2c.send(b'\x07c\x80', self._address)
        self._i2c.send(b'\x07d\xc8', self._address)
        self._i2c.send(b'\x07e\x82', self._address)
        self._i2c.send(b'\x07f\xb4', self._address)
        
    def reset(self):
        self._i2c.send(b'\x80\x63', self._address)
        
    def switch_on(self):
        self._i2c.send(b'\x5e\xbc', self._address)

    def _read_keys(self, line):
        self._i2c.send(b'\x00', self._address)
        self._i2c.recv(self._buffer, self._address)
        keycode = (self._buffer[1] & 0x1f) << 8 | self._buffer[0]

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
