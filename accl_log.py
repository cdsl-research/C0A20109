from machine import Pin, I2C, RTC
import utime
import urequests
import ujson
import time

class AE_BMX055:
    def __init__(self, i2c, *, addr_accel=25, debug=False):
        self.__i2c_wait_time = 200
        self.__i2c = i2c
        self.__addr_accel = addr_accel
        self.__debug = debug

        self.__init_accel()


    @property
    def accel(self):
        data = [None] * 6
        for i in range(6):
            # Read 6 bytes of data
            # xAccl lsb, xAccl msb, yAccl lsb, yAccl msb, zAccl lsb, zAccl msb
            data[i] = self.__read_1byte(addr=self.__addr_accel, register=(2 + i))

        if self.__debug:
            print('AE_BMX055.accel raw i2c data:', [hex(x) for x in data])

        # Convert the data to 12-bits
        xAccl = ((data[1] * 256) + (data[0] & 0xF0)) / 16
        if xAccl > 2047:
            xAccl -= 4096
        yAccl = ((data[3] * 256) + (data[2] & 0xF0)) / 16
        if yAccl > 2047:
            yAccl -= 4096
        zAccl = ((data[5] * 256) + (data[4] & 0xF0)) / 16
        if zAccl > 2047:
            zAccl -= 4096

        xAccl = xAccl * 0.0098  # renge +-2g
        yAccl = yAccl * 0.0098  # renge +-2g
        zAccl = zAccl * 0.0098  # renge +-2g

        return xAccl, yAccl, zAccl

    def __init_accel(self):
        print("init_accel")
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x0F, b'\x03')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x10, b'\x08')
        time.sleep_ms(self.__i2c_wait_time)

        self.__i2c.writeto_mem(self.__addr_accel, 0x11, b'\x00')
        time.sleep_ms(self.__i2c_wait_time)


    def __read_1byte(self, *, addr, register):
        return int.from_bytes(self.__i2c.readfrom_mem(addr, register, 1), 'big')

# ----- ----- ----- ----- ----- #
def write_data(file_path,time,x,y,z):
    # データを追記
    data_string = '{},{:>+13.4f},{:>+13.4f},{:>+13.4f}\n'.format(time,x, y, z)
    f = open(file_path, 'a')
    f.write(str(data_string))
    f.close()

def write_line(file_path):
    # ラインを追記
    f = open(file_path, 'a')
    f.write("time, x, y, z\n")
    
    f.close()

I2C_SCL_PIN = 22
I2C_SDA_PIN = 21

p_scl = Pin(I2C_SCL_PIN, Pin.IN, Pin.PULL_UP)
p_sda = Pin(I2C_SDA_PIN, Pin.IN, Pin.PULL_UP)
i2c = I2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))

bmx055 = AE_BMX055(i2c)

accl_path = "accl.csv"
write_line(accl_path)

while True:
    time_data = utime.ticks_ms() / 1000
    # BMX055 加速度の読み取り
    xAccl, yAccl, zAccl = bmx055.accel
    print('Accl= ({:>+13.4f}, {:>+13.4f}, {:>+13.4f})'.format(xAccl, yAccl, zAccl))
    write_data(accl_path,time_data,xAccl,yAccl,zAccl)
    #time.sleep_ms(100)
