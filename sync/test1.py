
class A:
    def __init__(self,d):
        self.d = d

d1 = {"a":1,"b":2}
d2 = d1

d1['c'] = 3

a = A(d2)

print(d2)
print(a.d)

