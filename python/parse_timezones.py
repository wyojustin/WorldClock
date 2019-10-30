from __future__ import print_function
import arrow

fn = "timezones.csv"
lines = open(fn).readlines()
arrow_time = arrow.get()

all = []
for line in lines[1:]:
    line = line.strip()
    line = line.split(',')
    if line[4].strip() != "Deprecated":
        s = "%30s %20s %s" % (line[2], line[2].split('/')[-1], arrow_time.to(line[2]))
        offset = s.split()[2][-6:]
        offset = offset.split(':')
        offset = int(offset[0]) * 60 + int(offset[1])
        all.append((offset, s))
all.sort()
for row in all:
    tz = row[1].split()[0]
    if '/' not in tz:
        tz = '%s/%s' % (tz, tz)
    print('%40s %20s' % (tz, tz.split('/')[1]))
