from __future__ import print_function
import arrow

fn = "timezones.csv"
lines = open(fn).readlines()
arrow_time = arrow.get()
for line in lines[1:]:
    line = line.strip()
    line = line.split(',')
    if line[4].strip() != "Deprecated":
        s = "%30s %20s %s" % (line[2], line[2].split('/')[-1], arrow_time.to(line[2]))
        print(s.replace('-', '<'))
