"""
`seeed_hm3301`
================================================================================

CircuitPython library for Seeed HM3301 PM laser dust sensor


* Author(s): Ryan Agius

Implementation Notes
--------------------

**Hardware:**

* `Seeed Grove HM3301 PM Laser Dust Sensor <https://www.seeedstudio.com/Grove-Laser-PM2-5-Sensor-HM3301.html>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""


import time
import math
from micropython import const

try:
    import struct
except ImportError:
    import ustruct as struct

#__version__ = "1.0.00"

#    I2C ADDRESS/BITS/SETTINGS
#    -----------------------------------------------------------------------
_HM3301_ADDRESS = const(0x40)

_HM3301_CHIPID = bytearray.fromhex("001C")
_HM3301_DATA_SIZE = 29

def _read16(arr):
    """Parse an unsigned 16-bit value as an integer."""
   
    return arr[0] << 8 | arr[1]

class Seeed_HM3301:
    """Driver from HM3301 Particulate Matter sensor

    :param int refresh_rate: Maximum number of readings per second. Faster property reads
      will be from the previous reading."""

    def __init__(self, *, refresh_rate=10):
        """Check the BME680 was found, read the coefficients and enable the sensor for continuous
        reads."""

        # Check device ID.
        chip_id = self._read()[2:4]
   
        if chip_id != _HM3301_CHIPID:
            raise RuntimeError("Failed to find HM3301! Chip ID = " + chip_id.hex())

        self._PM_1_0_conctrt_std = None
        self._PM_2_5_conctrt_std = None
        self._PM_10_conctrt_std = None
        self._PM_1_0_conctrt_atm = None
        self._PM_2_5_conctrt_atm = None
        self._PM_10_conctrt_atm = None

        self._last_reading = 0
        self._min_refresh_time = 1 / refresh_rate

    def check_crc(self, data):
        """Checks the crc of the data packet, retruns True if correct, False otherwise"""

        sum = 0
        for i in range(_HM3301_DATA_SIZE-1):
            sum += data[i]
        sum = sum & 0xff

        return (sum==data[28])

    @property
    def PM_1_0_conctrt_std(self):
        """The standard concentration of PM1.0 particles in ug/m3."""
        self._perform_reading()
        return self._PM_1_0_conctrt_std 

    @property
    def PM_2_5_conctrt_std(self):
        """The standard concentration of PM2.5 particles in ug/m3."""
        self._perform_reading()
        return self._PM_2_5_conctrt_std 


    @property
    def PM_10_conctrt_std(self):
        """The standard concentration of PM10 particles in ug/m3."""
        self._perform_reading()
        return self._PM_10_conctrt_std 

    @property
    def PM_1_0_conctrt_atm(self):
        """The atmospheric concentration of PM1.0 particles in ug/m3."""
        self._perform_reading()
        return self._PM_1_0_conctrt_atm

    @property
    def PM_2_5_conctrt_atm(self):
        """The atmospheric concentration of PM2.5 particles in ug/m3."""
        self._perform_reading()
        return self._PM_2_5_conctrt_atm 

    @property
    def PM_10_conctrt_atm(self):
        """The atmospheric concentration of PM10 particles in ug/m3."""
        self._perform_reading()
        return self._PM_10_conctrt_atm

    def _perform_reading(self):
        """Perform a single-shot reading from the sensor and fill internal data structure for
        calculations"""

        if time.monotonic() - self._last_reading < self._min_refresh_time:
            return

        data = self._read(_HM3301_DATA_SIZE)

        self._last_reading = time.monotonic()

        self._PM_1_0_conctrt_std = _read16(data[4:6])
        self._PM_2_5_conctrt_std = _read16(data[6:8])
        self._PM_10_conctrt_std = _read16(data[8:10])
        self._PM_1_0_conctrt_atm = _read16(data[10:12])
        self._PM_2_5_conctrt_atm = _read16(data[12:14])
        self._PM_10_conctrt_atm = _read16(data[14:16])

    def _read(self, length):
        raise NotImplementedError()

    def _write(self, register, values):
        raise NotImplementedError()

class Seeed_HM3301_I2C(Seeed_HM3301):
    """Driver for I2C connected HM3301.

    :param ~busio.I2C i2c: The I2C bus the HM3301 is connected to.
    :param int address: I2C device address. Defaults to :const:`0x40`
    :param bool debug: Print debug statements when `True`. Defaults to `False`
    :param int refresh_rate: Maximum number of readings per second. Faster property reads
      will be from the previous reading.

    **Quickstart: Importing and using the HM3301**

        Here is an example of using the :class:`HM3301_I2C` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import seeed_hm3301

        Once this is done you can define your `busio.I2C` object and define your sensor object

        .. code-block:: python

            i2c = busio.I2C(board.SCL, board.SDA)   # uses board.SCL and board.SDA
            hm3301 = seeed_hm3301.Seeed_HM3301_I2C(i2c)

        Now you have access to the :attr:`PM_1_0_conctrt_std`, :attr:`PM_2_5_conctrt_std`,
        :attr:`PM_10_conctrt_std`, :attr:`PM_1_0_conctrt_atm`, :attr:`PM_2_5_conctrt_atm`,
        :attr:`PM_10_conctrt_atm` attributes

        .. code-block:: python

            PM_2_5_concentration = hm3301.PM_2_5_conctrt_std

    """

    def __init__(self, i2c, address=0x40, debug=False, *, refresh_rate=10):
        """Initialize the I2C device at the 'address' given"""
        from adafruit_bus_device import (  # pylint: disable=import-outside-toplevel
            i2c_device,
        )

        self._i2c = i2c_device.I2CDevice(i2c, address)
        self._debug = debug
        super().__init__(refresh_rate=refresh_rate)

    def _read(self, length=_HM3301_DATA_SIZE):
        """Returns an array of 'length' bytes from the 'register'"""
        with self._i2c as i2c:
            result = bytearray(length)
            i2c.readinto(result)

            if self._debug:
                print("\t$%02X => %s" % (register, [hex(i) for i in result]))

            return result



