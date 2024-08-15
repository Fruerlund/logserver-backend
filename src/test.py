

STRING = b"ABC"

X = bytearray(STRING)
Y = bytearray(b"DEF\x00\x00\x00\x00") + X
#Y = X.count()
Z = len(Y)

print(Y.decode("ascii"))


String = ""
for b in X:
    String = String + chr(b)

print("YEET")
