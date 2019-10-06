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

def setPixel(x, y, canvas, color):
    graphics.DrawLine(canvas, x, y, x, y, color)
    
def bigDigit(x, y, digit, canvas, color):
  if(0 <= digit and digit < 10):
      for col in range(8):
          for row in range(16):
	      if((digits.digits8x16[digit, row] >> col) & 1):
                  setPixel(col + x, row + y, canvas, color)

def middleDigit(x, y, digit, canvas, color):
  if(digit < 10):
      for col in range(7):
          for row in range(11):
	      _row = 11 - row - 1
	      _col = 7 - col - 1
	      if((digits.digits7x11[digit, _row] >> _col) & 1):
                  setPixel(col + x, row + y, canvas, color)
def littleDigit(x, y, digit, canvas, color):
    if(digit < 13):
        for col in range(4):
            for row in range(7):
	        if((digits.digits4x7[digit, col] >> row) & 1):
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
      if(hh != 12):
           hh = hh % 12
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

def bigTime(current_time, start_x, start_y, canvas, color, am_pm=True, label=None, offset_str=None):
  hh, mm, ss = unix2hms(current_time)
  colen = (ss % 2) == 0
  W = 10
  H = 22
  if am_pm:
      pass
      am_pm = int(hh > 12)
      # littleDigit(start_x + 4 * 5,  start_y, 10 + am_pm, canvas, color) ## A or P
      # littleDigit(start_x + 5 * 5 - 1,  start_y, 12, canvas, color) # M
      if(hh != 12):
           hh = hh % 12
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
          graphics.DrawText(canvas, font_5x7, start_x + 20, start_y + 7 + 7 * i, color, label[i].upper())
          #littleChar(start_x + 20, start_y + 5 + 6 * i, label[i], canvas, color)
  if offset_str:
      for i in range(len(offset_str)):
          offset_str = offset_str.replace('-', '|')
          graphics.DrawText(canvas, font_5x7, start_x + 26, start_y + 7 + 7 * i, color, offset_str[i].upper())
      
             
def littleChar(x, y, char, canvas, color):
  idx = ord(char) - 32;
  pixels = fonts.font_5x6[idx];
  if(idx < 96):
      for col in range(5):
          for row in range(5):
	      if((pixels[col] >> (row+2)) & 1):
                  setPixel(col + x, row + y - 5, canvas, color)

def little3Code(code, start_x, start_y, canvas, color):
    littleChar(start_x +  0, start_y, code[0], canvas, color)
    littleChar(start_x +  6, start_y, code[1], canvas, color)
    littleChar(start_x + 12, start_y, code[2], canvas, color)
    
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

class Little3Code(Sprite):
    def __init__(self, x, y, code, color):
        Sprite.__init__(self, x, y)
        self.code = code
        self.color = color
        
    def draw(self, canvas):
        little3Code(self.code, self.x, self.y, canvas, self.color)
        
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
        text = '00:00:00'
        self.timezone = timezone
        Sprite.__init__(self, x, y)
        self.color = color

    def draw(self, canvas, arrow_tm):
        #now = time.localtime() + self.local_offset
        #self.text = "%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
        # self.text = "%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
        tm = arrow_tm.to(self.timezone).timetuple()
        now = tm.tm_hour * 3600 + tm.tm_min * 60 + tm.tm_sec
        littleTime(now, self.x, self.y, canvas, self.color)
        #now = time.localtime(time.time() + self.local_offset)
        #ss = now.tm_sec
        #mm = now.tm_min
        #hh = now.tm_hour
        #self.text = "%02d:%02d:%02d" % (hh, mm, ss)
                
        #Text.draw(self, canvas)
        
class LittleClock(Sprite):
    def __init__(self, x, y, color, timezone):
        Sprite.__init__(self, x, y)
        self.color = color
        self.timezone = timezone

    def draw(self, canvas, arrow_tm):
        tm = arrow_tm.to(self.timezone).timetuple()
        now = tm.tm_hour * 3600 + tm.tm_min * 60 + tm.tm_sec
        littleTime(now, self.x, self.y, canvas, self.color)

class BigClock(Sprite):
    def __init__(self, x, y, color, timezone):
        Sprite.__init__(self, x, y)
        self.color = color
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
        bigTime(now, self.x, self.y, canvas, self.color, label=self.label, offset_str=offset_str)
    
class WorldClock(Sprite):
    def __init__(self, x, y, color, timezones):
        self.start_x = x
        self.start_y = y
        self.color = color
        self.timezones = timezones
        #self.clocks = [
        #    Clock(x, y + 1 * (7 + 8) - 2, color, timezones[0][0]),
        #    Clock(x, y + 2 * (7 + 8) - 2, color, timezones[1][0]),
        #    Clock(x, y + 3 * (7 + 8) - 2, color, timezones[2][0]),
        #]
        #self.codes = [
        #    Little3Code(x + 3, y + 5 + 0 * (7 + 8), timezones[0][1], color),
        #    Little3Code(x + 3, y + 5 + 1 * (7 + 8), timezones[1][1], color),
        #    Little3Code(x + 3, y + 5 + 2 * (7 + 8), timezones[2][1], color),
        #    ]
        self.clocks = [LittleClock(x, y + (i + 1) * (7 + 8) - 2, color, timezones[i][0])
                       for i in range(len(timezones))[:4]]
        self.codes = [Little3Code(x + 3, y + 5 + i * (7 + 8), timezones[i][1], color)
                      for i in range(len(timezones))[:4]]

    def draw(self, canvas):
        arrow_tm = arrow.get()

        for clock in self.clocks:
            clock.draw(canvas, arrow_tm)
        for code in self.codes:
            code.draw(canvas)
    def scroll_up():
        self.timezones = [self.timezones[0]] + self.timezones[2:] + [self.timezones[1]]
        self.clocks = [LittleClock(x, y + (i + 1) * (7 + 8) - 2, color, self.timezones[i][0])
                       for i in range(len(timezones))[:4]]
        self.codes = [Little3Code(x + 3, y + 5 + i * (7 + 8), self.timezones[i][1], color)
                      for i in range(len(timezones))[:4]]
    
mode_idx = 0
tom_thumb = graphics.Font()
tom_thumb.LoadFont(os.path.join(font_dir, "tom-thumb.bdf"))
font_5x7 = graphics.Font()
font_5x7.LoadFont(os.path.join(font_dir, "5x7.bdf"))

RED = graphics.Color(0, 0, 255)
GREEN = graphics.Color(  0, 255, 0)
BLUE = graphics.Color(  255, 0, 0)

class RunClock(MatrixBase):
    def __init__(self, *args, **kwargs):
        super(RunClock, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    def run(self):
        print("Press N for next, Q to quit")

        offscreen_canvas = self.matrix.CreateFrameCanvas()

        timezones = [['America/Los_Angeles', 'SFO'],
                     ['America/Denver', 'WYO'],
                     ['America/New_York', 'BOS'],
                     ['Asia/Kolkata', 'MUM'],
                     ['Asia/Kolkata', 'MUM'],
        ]
        #test_text = Text(21, 13, "AM", BLUE, tom_thumb)
        
        world_clock = WorldClock(0, 0, BLUE, timezones)
        big_clock = BigClock(0, 0, GREEN, ['America/New_York', ' New York'])
        big_clocks = [
            BigClock(0, 0, GREEN, ['GMT', 'Zulu']),
            BigClock(0, 0, BLUE, ['Europe/London', 'London']),
            BigClock(0, 0, GREEN, ['America/New_York', 'New York']),
            BigClock(0, 0, BLUE, ['America/Denver', 'Denver']),
            BigClock(0, 0, GREEN, ['America/Los Angeles', 'Los Angeles'])]
        

        modes = big_clocks + [world_clock]
        def read_command():
            result = select.select([sys.stdin,],[],[],0.0)[0]
            if result:
                out = sys.stdin.readline().strip()
            else:
                out = None
            return out
        def next_display():
            global mode_idx
            mode_idx = (mode_idx+1) % (len(modes))
        while True:
            offscreen_canvas.Clear()
            modes[mode_idx].draw(offscreen_canvas)
            #middleDigit(10, 30, 7, offscreen_canvas, BLUE)
            #test_text.draw(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            
            command = read_command()
            if command:
                command = command.upper()
                if command == 'N':
                    next_display()
                if command == 'Q':
                    break
            time.sleep(0.05)
# Main function
if __name__ == "__main__":
    run_clock = RunClock()
    if (not run_clock.process()):
        run_text.print_help()
