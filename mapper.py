#!/usr/bin/env python
from _io import StringIO
    

import sys
import re
# input comes from STDIN (standard input)
for line in sys.stdin:
#for line in csv.reader():
    list = line.split(',')
    business_id=list[0]
    l=re.findall('"(.*)"', line)

    
   # keyAndValue=[business_id,review]
    
    print('%s\t%s' % (business_id, l))
    #X=[re.split(r', (?=(?:"[^"]*?(?: [^"]*)*))|~ (?=[^"~]+(?:,|$))', line)]

