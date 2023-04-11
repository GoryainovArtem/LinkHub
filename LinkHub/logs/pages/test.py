import re

from ....links. import Project


tags = Project.objects.filter(id__in=[1, 3]).values('theme')
print(tags)


import pandas as pn
with open('2.log') as file:
    pattern = r'., DEBUG,'
    data = [line.strip('\n') for line in file.readlines()]
    data = [line for line in data if re.search(pattern, line)]

