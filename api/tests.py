from django.test import TestCase
import time

# Create your tests here.
print(time.time())

a = {'k1': 1, 'k2': 2}
b = {'k2': 3, 'k4': 4}
a.update(b)  # 字典的 update方法（把b的键值对跟新到a中，如果a有这个键就覆盖）

print(a)