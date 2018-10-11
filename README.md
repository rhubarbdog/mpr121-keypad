mpr121 keypad

`*_keypad.py` defines one class `KEYPAD` for user programs. The class has 3 parameters `i2c` (the i2c bus to use), `rq_pin` (the requset pin) and `address` (the i2c device address, this will be 0x5a, 0x5b, 0x5c or 0x5d).
The `KEYPAD` object is made up of 2 types of object.  12 `KEY` objects which are accessed via the dictionary `KEYPAD.key` using the symbol on the keypad as the lookup symbol. And a `PROXIMITY` object (`KEYPAD.keypad`).
The `PROXIMITY` object has 2 user methods
<table>
<tr><td>Method</td><td>Type</td></tr>
<tr><td>`.is_near()`</td><td>boolean</td><td>is a finger near the keypad.</td></tr>
<tr><td>`.was_near()`</td><td>boolean</td><td>has anything been near the keypad since the `.was_near()` method was last executed.</td></tr>
</table>
`KEY` objects have 3 user methods
<table>
<tr><td>Method</td><td>Type</td></tr>
<tr><td>`.is_pressed()`</td><td>boolean</td><td>returns True if the key is being pressed.</td></tr>
<tr><td>`.was_pressed()`</td><td>boolean</td><td>returns True if the key has been pressed since the last call to the `.was_pressed()` method.</td></tr>
<tr><td>`.get_presses()`</td><td>integer</td><td>returns the number of times the key has been pressed since the last call to the `'get_presses()` method.</td></tr>
</table>

With the exception of `microbit_keypad.py`, object `KEYPAD` has no user methods KEY states and PROXIMITY to the sensor are accessed by methods on the dictionay `KEYPAD.key` or object `KEYPAD.keypad`.
Because the microbit can't react to pin events such as a rising edge programs should use method `KEYPAD.sleep()` rather than function `microbit.sleep()`. Method `KEYPAD.sleep()` polls the request pin and if necessary reads the keypad and updates the `PROXIMITY` and `KEY` objects. If your program has no sleeps, it should include frequent calls to method `KEYPAD.sleep(0)`, which will poll the request pin and update the internal objects if required.