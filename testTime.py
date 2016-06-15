import time
import random

a = set()
a.add(1)
a.add(2)
a.add(3)
b = set()
b.add(2)
b.add(3)
b.add(4)
c = a.union(b)
print len(c)