string = str(b'0-0-0-0-0-0-0-0-0\n')
string = str(b'70-70-70-70-70-70-20-20-70-70\n')
print(string)
print(string[2:-3])

data = string
massControll = [int(i) for i in ((str(data)[2:-3]).split('-'))]
print(massControll)

'''
datastr = str(data)[2:-3]
massControll = str(datastr).split('-')
massControll = [int(i) for i in massControll]
print(massControll)
'''
print(len(b'70-70-70-70-70-70-70-70\n'))