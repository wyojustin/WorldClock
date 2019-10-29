import struct
import time
import smbus2
 
I2C = smbus2.SMBus(1)
NAVKEY_ADDR = 0x10

FLOAT_DATA = 0x01
INT_DATA = 0x00
WRAP_ENABLE = 0x02
WRAP_DISABLE = 0x00
DIRE_LEFT = 0x04
DIRE_RIGHT = 0x00
IPUP_DISABLE = 0x08
IPUP_ENABLE = 0x00
CLK_STRECH_ENABLE = 0x10
CLK_STRECH_DISABLE = 0x00
EEPROM_BANK1 = 0x20
EEPROM_BANK2 = 0x00
RESET = 0x80

REG_GCONF = 0x00
REG_GP1CONF = 0x01
REG_GP2CONF = 0x02
REG_GP3CONF = 0x03
REG_INTCONFB2 = 0x04
REG_INTCONFB1 = 0x05
REG_STATUSB2 = 0x06
REG_STATUSB1 = 0x07
REG_SSTATUS = 0x08
REG_FSTATUS = 0x09
REG_CVALB4 = 0x0A
REG_CVALB3 = 0x0B
REG_CVALB2 = 0x0C
REG_CVALB1 = 0x0D
REG_CMAXB4 = 0x0E
REG_CMAXB3 = 0x0F
REG_CMAXB2 = 0x10
REG_CMAXB1 = 0x11
REG_CMINB4 = 0x12
REG_CMINB3 = 0x13
REG_CMINB2 = 0x14
REG_CMINB1 = 0x15
REG_ISTEPB4 = 0x16
REG_ISTEPB3 = 0x17
REG_ISTEPB2 = 0x18
REG_ISTEPB1 = 0x19
REG_GP1REG = 0x1A
REG_GP2REG = 0x1B
REG_GP3REG = 0x1C
REG_DPPERIOD = 0x1D
REG_FADEGP = 0x1E
REG_GAMMAGP1 = 0x1F
REG_GAMMAGP2 = 0x20
REG_GAMMAGP3 = 0x21
REG_IDCODE = 0x70
REG_VERSION = 0x71
REG_EEPROMS = 0x80


SUPR = '<Up release>'
SUPP = '<Up press>'
SDNR = '<Down release>'
SDNP = '<Down press>'
SRTR = '<Right release>'
SRTP = '<Right press>'
SLTR = '<Left release>'
SLTP = '<Left press>'
SCTRR = '<Central release>'
SCTRP = '<Central press>'
SCTRDP = '<Central double>'
SRINC = '<Rotary increment>'
SRDEC = '<Rotary decrement>'
SRMAX = '<Rotaty max>'
SRMIN = '<Rotary min>'
SINT2 = '<Secondary interrupt>'

istatus_map = [  SUPR,  SUPP,   SDNR,  SDNP,  SRTR,  SRTP,  SLTR,  SLTP,
                SCTRR, SCTRP, SCTRDP, SRINC, SRDEC, SRMAX, SRMIN, SINT2]
#istatus_map = map(str, range(16))

def byte2bin(b):
    out = ''
    for i in range(8):
        out += str((b >> i) & 1)
    return out

def bytes2bin(bytes):
    out = ''
    for b in bytes[::-1]:
        out += byte2bin(b)
    return out

class I2CNavKey:
    def __init__(self, addr):
        self.addr = addr

        conf = INT_DATA | WRAP_ENABLE | DIRE_RIGHT | IPUP_ENABLE
        self.writeNavKey(REG_GCONF, conf);
        
        self.writeCounter(0); #/* Reset the counter value */
        self.writeMin(0); #/* Set the minimum threshold */
        self.writeMax(0); #/* Set the maximum threshold*/ ### not working
        self.writeStep(1); #/* Set the step to 1*/
        self.callbacks = {}
    def bindkey(self, event, callback):
        self.callbacks[event] = callback
    def writeInterruptConfig(self, interrupt):
        self.writeNavKey(REG_INTCONFB2, interrupt);
    def writeCounter(self, value):
        self.writeNavKey(REG_CVALB4, value);
    def writeMax(self, max):
        self.writeNavKey(REG_CMAXB4, max);
    def writeMin(self, min):
        self.writeNavKey(REG_CMAXB4, min);
    def writeStep(self, step):
        self.writeNavKey(REG_ISTEPB4, step);
    def writeNavKey(self, reg, byte):
        I2C.write_byte_data(self.addr, reg, byte)
    def readNavKey(self, reg):
        return I2C.read_byte_data(self.addr, reg)


    def read_all(self):
        return I2C.read_i2c_block_data(self.addr, 0, 32) + I2C.read_i2c_block_data(self.addr, 32, 32)
    def get_events(self):
        data = I2C.read_i2c_block_data(self.addr, REG_STATUSB2, 2)
        #data = I2C.read_i2c_block_data(self.addr, REG_CVALB4, 4)
        events = ''.join([byte2bin(d) for d in data[::-1]])
        out = []
        for i, c in enumerate(events):
            if c == '1':
                out.append(istatus_map[i])
        return out

    def readCounterInt(self):
        return self.readNavKeyInt(REG_CVALB4)
    def readNavKeyInt(self, reg):
        bytes = ''.join([chr(b) for b in I2C.read_i2c_block_data(self.addr, reg, 4)])
        return struct.unpack('<i', bytes)
    def react(self):
        events = self.get_events()
        for event in events:
            if event in self.callbacks:
                self.callbacks[event]()

nav = I2CNavKey(NAVKEY_ADDR)

def test_cval():
    for count in range(1023):
        print '%6d' % count,
        nav.readCounterInt()
        nav.writeCounter(256+count); #/* Reset the counter value */
        time.sleep(.01)
        count += 1

if __name__ == '__main__':
    while 1:
        def central_click():
            print 'Central click callback()'
        def right_click():
            print 'Right click callback()'

        nav.bindkey(SCTRR, central_click)
        nav.bindkey('<Right release>', right_click)
        nav.react()

        time.sleep(.1)
