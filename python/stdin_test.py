import sys
import select
while 1:
    result = select.select([sys.stdin,],[],[],0.0)[0]
    if result:
        print(sys.stdin.readline().strip())
        
