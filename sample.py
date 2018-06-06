channel="Party"
users=["sita"]

#usr1="hello"
#usr2="world"
#test=(usr1,usr2)

print(test[0])

print(test)

mydict={channel:users}

mydict[channel].append("gita")

if channel in mydict:
	mydict["Zoo"]=["binita"]
else:
	print("NO")

mydict["Zoo"].append("raute")
print(mydict)
