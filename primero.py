from utils import flatten
from sys import argv

def strobograficos(n, order):
    if n == 0:
        return [""]
    if n == 1:
        return ["1", "0", "8"]
    medio = strobograficos(n-2, order)
    numeros = []
    for j in medio:
        if n != order:
            numeros.append("0" + j + "0")
        numeros.append("8" + j + "8")
        numeros.append("1" + j + "1")
        numeros.append("9" + j + "6")
        numeros.append("6" + j + "9")
    return numeros

def reto1(num1,num2):
    n=len(str(num2))+1
    nums=[]
    for i in range(1,n):
        numero=strobograficos(i, i)
        nums.append(numero)
    nums=flatten(nums)
    nums=[int(x) for x in nums if num1<= int(x) <= num2]
    if num2<num1:
        raise NameError('Se ingreso un numero no valido el primer numero debe ser menor al segundo')
    return sorted(nums),len(nums)


if __name__ == "__main__":
    num1,num2= argv[1:]
    num1,num2=int(num1),int(num2)
    z=reto1(num1,num2)
    print("Tenemos "+str(z[1])+" numeros invertidos validos, los cuales son "+', '.join([str(i) for i in z[0]]))
    #print(z)