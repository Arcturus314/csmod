c1 = ["N", "x"]
c2 = ["E", "x"]
c3 = ["W", "x"]
c4 = ["S", "x"]

returnList = []

for a in c1:
    for b in c2:
        for c in c3:
            for d in c4:
                string = a+b+c+d
                print(string)
                returnList += str(string)

print(returnList)
