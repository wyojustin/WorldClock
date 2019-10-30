#!/usr/bin/env python
# Display a runtext with double-buffering.
import os.path
import sys
import select
from matrixbase import MatrixBase
from rgbmatrix import graphics
import time
import arrow

import digits
import fonts
from constants import font_dir
from constants import RED, GREEN, BLUE, PURPLE

from I2CNavKey import nav

def setPixel(x, y, canvas, color):
    graphics.DrawLine(canvas, x, y, x, y, color)
    
def bigDigit(x, y, digit, canvas, color):
  if(0 <= digit and digit < 10):
      for col in range(8):
          for row in range(16):
	      if((digits.digits8x16[digit][row] >> col) & 1):
                  setPixel(col + x, row + y, canvas, color)

def middleDigit(x, y, digit, canvas, color):
  if(digit < 10):
      for col in range(7):
          for row in range(11):
	      _row = 11 - row - 1
	      _col = 7 - col - 1
	      if((digits.digits7x11[digit][_row] >> _col) & 1):
                  setPixel(col + x, row + y, canvas, color)
def littleDigit(x, y, digit, canvas, color):
    if(digit < 13):
        for col in range(4):
            for row in range(7):
	        if((digits.digits4x7[digit][col] >> row) & 1):
                    setPixel(col + x, row + y, canvas, color)

def unix2hms(unix):
    spm = int(unix) % 86400;
    hh = spm / 3600;
    mm = ((spm - hh * 3600) / 60); 
    ss = spm % 60;
    return hh, mm, ss

def littleTime(current_time, start_x, start_y, canvas, color, am_pm=True):
  hh, mm, ss = unix2hms(current_time)
  colen = (ss % 2) == 0
  start_y -= 7 ## reference to baseline (not top)
  if am_pm:
      am_pm = int(hh > 12)
      littleDigit(start_x + 4 * 5,  start_y, 10 + am_pm, canvas, color) ## A or P
      # littleDigit(start_x + 5 * 5 - 1,  start_y, 12, canvas, color) # M
      hh = (hh - 1) % 12 + 1

  else:
      hh %= 24

  if(hh > 9):
    littleDigit(start_x + 0 * 5 - 1,  start_y, hh//10, canvas, color)

  littleDigit(start_x + 1 * 5 - 1,  start_y, hh % 10, canvas, color)

  if colen:
      setPixel(start_x + 9, start_y + 2, canvas, color)
      setPixel(start_x + 9, start_y + 4, canvas, color);

  littleDigit(start_x + 2 * 5 + 1,  start_y, mm/10, canvas, color);
  littleDigit(start_x + 3 * 5 + 1,  start_y, mm%10, canvas, color);

def bigTime(current_time, start_x, start_y, canvas, color, am_pm=True, label=None, offset_str=None, color2=None):
  if color2 is None:
      color2 = color
  hh, mm, ss = unix2hms(current_time)
  colen = (ss % 2) == 0
  W = 10
  H = 22
  if am_pm:
      pass
      am_pm = int(hh > 12)
      # littleDigit(start_x + 4 * 5,  start_y, 10 + am_pm, canvas, color) ## A or P
      # littleDigit(start_x + 5 * 5 - 1,  start_y, 12, canvas, color) # M
      hh = (hh - 1) % 12 + 1

  else:
      hh %= 24

  if(hh > 9):
    bigDigit(start_x,  start_y, hh//10, canvas, color)

  bigDigit(start_x + W,  start_y, hh % 10, canvas, color)

  def colen(my_x, my_y):
      setPixel(my_x + 5, my_y + H - 3, canvas, color)
      setPixel(my_x + 6, my_y + H - 4, canvas, color);
      setPixel(my_x + 5, my_y + H - 4, canvas, color)
      setPixel(my_x + 6, my_y + H - 3, canvas, color);

      setPixel(my_x + 11, my_y + H - 3, canvas, color)
      setPixel(my_x + 12, my_y + H - 4, canvas, color);
      setPixel(my_x + 11, my_y + H - 4, canvas, color)
      setPixel(my_x + 12, my_y + H - 3, canvas, color);
  if ss % 2 == 1:
      colen(start_x, start_y)
      colen(start_x, start_y + H)
  bigDigit(start_x    ,  start_y + 1 * H, mm/10, canvas, color);
  bigDigit(start_x + W,  start_y + 1 * H, mm%10, canvas, color);
  bigDigit(start_x    ,  start_y + 2 * H, ss/10, canvas, color);
  bigDigit(start_x + W,  start_y + 2 * H, ss%10, canvas, color);
  if label:
      for i in range(len(label)):
          graphics.DrawText(canvas, font_5x7, start_x + 20, start_y + 7 + 7 * i, color2, label[i].upper())
          #littleChar(start_x + 20, start_y + 5 + 6 * i, label[i], canvas, color)
  if offset_str:
      for i in range(len(offset_str)):
          graphics.DrawText(canvas, font_5x7, start_x + 26, start_y + 7 + 7 * i, color2, offset_str[i].upper())
      
             
def littleChar(x, y, char, canvas, color):
  idx = ord(char) - 32;
  pixels = fonts.font_5x6[idx];
  if(idx < 96):
      for col in range(5):
          for row in range(5):
	      if((pixels[col] >> (row+2)) & 1):
                  setPixel(col + x, row + y - 5, canvas, color)

def littleCode(code, start_x, start_y, canvas, color):
    for i in range(len(code)):
        littleChar(start_x +  i * 6, start_y, code[i], canvas, color)
    
class Sprite:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def draw(self, canvas):
        pass
    def move(self, dxdy):
        dx, dy = dxdy
        self.x += dx
        self.y += dy
    def send_command(self, command):
        pass
class LittleCode(Sprite):
    def __init__(self, x, y, code, color):
        Sprite.__init__(self, x, y)
        self.code = code
        self.color = color
        
    def draw(self, canvas):
        littleCode(self.code, self.x, self.y, canvas, self.color)
        
class Text(Sprite):
    def __init__(self, x, y, text, color, font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
    def draw(self, canvas):
        return graphics.DrawText(canvas, self.font, self.x, self.y, self.color, self.text)

class ScrollText(Text):
    def __init__(self, x, y, text, color, font, speed=(-1, 0)):
        Text.__init__(self, x, y, text, color, font)
        self.speed = speed
    def draw(self, canvas):
        self.move(self.speed)
        len = Text.draw(self, canvas)
        if self.x + len < 0:
            self.x = canvas.width
        if self.x > canvas.width:
            self.x = 0
        if self.y < 0:
            self.y = canvas.height
        if self.y > canvas.height:
            self.y = 0
            
class LittleClock(Sprite):
    def __init__(self, x, y, color, timezone):
        Sprite.__init__(self, x, y)
        self.color = color
        self.timezone = timezone

    def draw(self, canvas, arrow_tm):
        if self.timezone == 'Local':
            tm = time.localtime()
        else:
            tm = arrow_tm.to(self.timezone).timetuple()
        now = tm.tm_hour * 3600 + tm.tm_min * 60 + tm.tm_sec
        littleTime(now, self.x, self.y, canvas, self.color)

class BigClock(Sprite):
    def __init__(self, x, y, color, timezone, color2=None):
        if color2 is None:
            color2 = color
        Sprite.__init__(self, x, y)
        self.color = color
        self.color2 = color2
        self.timezone = timezone
        self.label = self.timezone[1]

    def draw(self, canvas):
        arrow_tm = arrow.get().to(self.timezone[0])
        tm = arrow_tm.timetuple()
        utcoffset = arrow_tm.utcoffset().total_seconds()
        offset_hh = int(utcoffset / 3600)
        offset_mm = int((utcoffset % 3600) / 60)
        offset_str = "GMT %+02d%02d" % (offset_hh, offset_mm)
        now = tm.tm_hour * 3600 + tm.tm_min * 60 + tm.tm_sec
        bigTime(now, self.x, self.y, canvas, self.color, label=self.label, offset_str=offset_str, color2=self.color2)
    
class WorldClock(Sprite):
    def __init__(self, x, y, colors, timezones):
        self.x = x
        self.y = y
        self.colors = colors
        self.timezones = timezones
        self.color_offset = 0
        self.create_sprites()

        lines = open('timezones.txt').readlines()
        self.all_zones = [line.split() for line in lines[1:]]
        
    def create_sprites(self):
        self.codes = []
        self.clocks = []
        for i in range(len(self.timezones[:4])):
            if i == 0:
                color = PURPLE
            else:
                color = self.colors[(i + self.color_offset) % len(self.colors)]
            code = self.timezones[i][1][:5]
            half = len(code) * 3
            x = 16 - half
            self.codes.append(LittleCode(x, self.y + 5 + i * (7 + 8), self.timezones[i][1], color))
            self.clocks.append(LittleClock(self.x, self.y + (i + 1) * (7 + 8) - 2, color, self.timezones[i][0]))

    def draw(self, canvas):
        arrow_tm = arrow.get()

        for clock in self.clocks:
            clock.draw(canvas, arrow_tm)
        for code in self.codes:
            code.draw(canvas)
    def scroll_down(self):
        self.timezones = [self.timezones[0]] + [self.timezones[-1]] + self.timezones[1:-1]
        self.color_offset -= 1
        self.create_sprites()
    def scroll_up(self):
        self.timezones = [self.timezones[0]] + self.timezones[2:] + [self.timezones[1]]
        self.color_offset += 1
        self.create_sprites()

    def get_current_idx(self):
        current = self.timezones[1][0]
        current_idx = None
        for i, (tz, code) in enumerate(self.all_zones):
            if tz == current:
                current_idx = i
                break
        return current_idx
    
    def increment(self):
        # find current timezone
        # grab next timezone
        current_idx = self.get_current_idx()
        if current_idx:
            next = (current_idx + 1) % len(self.all_zones)
            tz, code = self.all_zones[next]
            self.timezones[1] = [tz, code]
            self.create_sprites()
        
    def decrement(self):
        # find current timezone
        # grab previous timezone
        current_idx = self.get_current_idx()
        if current_idx:
            prev = (current_idx -1) % len(self.all_zones)
            tz, code = self.all_zones[prev]
            self.timezones[1] = [tz, code]
            self.create_sprites()
            
    def send_command(self, command):
        for c in command:
            if c == 'R':
                self.scroll_up()
            if c == 'L':
                self.scroll_down()
            if c == 'I':
                self.increment()
            if c == 'K':
                self.decrement()
mode_idx = 0
tom_thumb = graphics.Font()
tom_thumb.LoadFont(os.path.join(font_dir, "tom-thumb.bdf"))
font_5x7 = graphics.Font()
font_5x7.LoadFont(os.path.join(font_dir, "5x7.bdf"))

BRIGHTNESS = [2,   3,   5,   6,   9,  12,  15,  21,  27,
              36,  48,  63,  84, 111, 146, 193, 255]

def brighter(b):
    idx = 0
    while idx < len(BRIGHTNESS) - 1 and BRIGHTNESS[idx] < b:
        idx += 1
    idx += 1
    out = BRIGHTNESS[idx]
    return out

def dimmer(b):
    idx = len(BRIGHTNESS) - 1
    while 1 < idx and BRIGHTNESS[idx] > b:
        idx -= 1
    idx -= 1
    out = BRIGHTNESS[idx]
    return out

quit = [False] ### lists are mutable, use instead of global quit
class RunClock(MatrixBase):
    def __init__(self, *args, **kwargs):
        super(RunClock, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")
        self.command_buffer = []
        nav.bindkey('<Up release>', lambda: self.add_cmd('U'))
        nav.bindkey('<Down release>', lambda: self.add_cmd('D'))
        nav.bindkey('<Central release>', lambda: self.add_cmd('C'))
        nav.bindkey('<Left release>', lambda: self.add_cmd('L'))
        nav.bindkey('<Right release>', lambda: self.add_cmd('R'))
        nav.bindkey('<Rotary increment>', lambda: self.add_cmd('I'))
        nav.bindkey('<Rotary decrement>', lambda: self.add_cmd('K'))

    def add_cmd(self, cmd):
        self.command_buffer.append(cmd)
        
    def run(self):
        print("Press N for next, Q to quit")

        offscreen_canvas = self.matrix.CreateFrameCanvas()

        wyozones = [
            ['Local', 'Bostn'],
#            ['America/New York', 'Bostn'],
            ['America/Los Angeles', 'Diego'],
            ['Asia/Shanghai', 'SHNZN'],
            ['Asia/Kolkata', 'MUMBI'],
        ]
        timezones = [['Local', 'LOCAL'],
                     # ['GMT', 'ZULU'],
                     ['Europe/London', 'LONDN'],
                     ['America/New_York', 'NY'],
                     ['America/Chicago', 'CHIGO'],
                     ['America/Denver', 'DENVR'],
                     ['America/Los Angeles', 'LA'],
                     ['Asia/Shanghai', 'SHNZN'],
                     ['Asia/Kolkata', 'MUMBI'],
        ]
        #test_text = Text(21, 13, "AM", BLUE, tom_thumb)
        
        zones = [('Local', 'LOCAL')]
        colors = [PURPLE]
        tz_txt = 'zonemap.txt'
        lines = open(tz_txt).readlines()
        for i, line in enumerate(lines[1:]):
            line = line.split()
            if line:
                code = line[0]
                city = line[1]
                color = [GREEN, BLUE][i % 2]
                zones.insert(1, (code, city))
                colors.insert(1, color)
        world_clocks = [
            WorldClock(0, 0, [BLUE, GREEN], timezones),
            WorldClock(0, 0, [BLUE, GREEN, RED], wyozones),
            WorldClock(0, 0, colors, zones)
            ]
        big_clock = BigClock(0, 0, GREEN, ['America/New_York', ' New York'], color2=BLUE)
        big_clocks = [
            BigClock(0, 0, GREEN, ['GMT', 'Zulu'], color2=BLUE),
            BigClock(0, 0, BLUE, ['Europe/London', 'London'], color2=GREEN),
            BigClock(0, 0, GREEN, ['America/New_York', 'New York'], color2=BLUE),
            BigClock(0, 0, BLUE, ['America/Denver', 'Denver'], color2=GREEN),
            BigClock(0, 0, GREEN, ['America/Los Angeles', 'Los Angeles'], color2=BLUE)]

        modes =  world_clocks + big_clocks
        def read_command():
            result = select.select([sys.stdin,],[],[],0.0)[0]
            if result:
                out = sys.stdin.readline().strip()
            else:
                out = ''
            nav.react()
            if self.command_buffer:
                out = out + ''.join(self.command_buffer)
                self.command_buffer = []
            return out
        def next_display():
            global mode_idx
            mode_idx = (mode_idx+1) % (len(modes))
        def prev_display():
            global mode_idx
            mode_idx = (mode_idx + len(modes) - 1) % (len(modes))
        while not quit[0]:
            offscreen_canvas.Clear()
            modes[mode_idx].draw(offscreen_canvas)
            #middleDigit(10, 30, 7, offscreen_canvas, BLUE)
            #test_text.draw(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            
            command = read_command()
            if command:
                for c in command.upper():
                    command = c
                    if command == 'C':
                        next_display()
                    elif command == 'P':
                        prev_display()
                    elif command == 'U' and self.matrix.brightness < 255:
                        self.matrix.brightness = brighter(self.matrix.brightness)
                    elif command == 'D' and self.matrix.brightness > 0:
                        self.matrix.brightness = dimmer(self.matrix.brightness)
                    elif command == 'Q':
                        quit[0] = True
                        break
                    else:
                        ## send command to active display
                        modes[mode_idx].send_command(command)
                    last_command = command
                time.sleep(0.05)
# Main function
if __name__ == "__main__":
    run_clock = RunClock()
    if (not run_clock.process()):
        run_text.print_help()
