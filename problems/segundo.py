from utils import flatten
from sys import argv

class PuzzleFrame:
    def __init__(self, state):
        self.state = state
        self.n=len(state[0])

    def show(self):
    #Muestra el Tablero
        sep = "|"
        floor = "----"
        print(floor * (self.n))
        for i in self.state:
            counter , puzzle = 0, sep
            while counter < len(i):
                puzzle += str(i[counter]).ljust(3) + sep
                counter += 1
            print(puzzle)
            print(floor * (self.n))
    def find_neighbors(self,m, i, j):
        # Encuentra los vecinos del 0
        n=len(m)
        if (i==0) & (j==0):
            nei=[m[0][j+1],m[1][j]]
        elif (i==n-1) & (j==0):
            nei=[m[n-2][j],m[n-1][j+1]]
        elif (i==0) & (j==n-1):
            nei=[m[i+1][j],m[i][j-1]]
        elif (i==n-1) & (j==n-1):
            nei=[m[i][j-1],m[i-1][j]]
        elif (i!=0)&(i!=n-1)&(j==0):
            nei=[m[i-1][j],m[i+1][j],m[i][j+1]]
        elif (i!=0)&(i!=n-1)&(j==n-1):
            nei=[m[i+1][j],m[i-1][j],m[i][j-1]]
        elif (j!=0)&(j!=n-1)&(i==n-1):
            nei=[m[i][j-1],m[i-1][j],m[i][j+1]]
        elif (j!=0)&(j!=n-1)&(i==0):
            nei=[m[i][j+1],m[i][j-1],m[i+1][j]]
        else:
            nei=[m[i+1][j],m[i][j+1],m[i][j-1],m[i-1][j]]
        return nei
    def Manhattan_distance(self,state):
        flattened = [item for sublist in state for item in sublist]
        solution = list(range(1, len(flattened)))+[0]
        mandistance = 0
    #distancia de manhattan (sacada de Geeks4Geeks)
        for element in flattened:
            distance = abs(solution.index(element) - flattened.index(element))
            xcoord, ycoord = distance//len(state[0]), distance%len(state[0])
            mandistance += xcoord + ycoord
        return mandistance

    def swap(self,state,nei):
        #Un movimiento
        n=len(state[0])
        flattened=flatten(state)
        zero=flattened.index(0)
        nei=flattened.index(nei)
        flattened[zero], flattened[nei] = flattened[nei], flattened[zero]
        return self.state_cons(flattened,n)

    def moves(self,state):
        #movimientos posibles
        storage  =  []
        n=len(state[0])
        pos0=[(i,state[i].index(0))  if 0 in state[i] else None for i in range(n)]
        i,j=next(item for item in pos0 if item is not None)
        neighbors=self.find_neighbors(state,i,j)
        for i in neighbors:
            posnei=[(j,state[j].index(i))  if i in state[j] else None for j in range(n)]
            l,m=next(item for item in posnei if item is not None)
            storage.append(self.swap(state,i))
        return storage
    def Astar(self,start, finish, heuristic):
        #Algoritmo A* (Path-finding)
        n = len(start)
        start , finish = start, finish
        pathstorage = [[heuristic(start), start]]  
        expanded = []
        expanded_nodes = 0
        while pathstorage:
            i = 0
            for j in range(1, len(pathstorage)):
                if pathstorage[i][0] > pathstorage[j][0]:
                    i = j
            path = pathstorage[i]
            pathstorage = pathstorage[:i] + pathstorage[i + 1:]
            finishnode = path[-1]
            if finishnode == finish:
                break
            if finishnode in expanded: continue
            for b in self.moves(finishnode):
                if b in expanded: continue
                newpath = [path[0] + heuristic(b) - heuristic(finishnode)] + path[1:] + [b]
                pathstorage.append(newpath)
                expanded.append(finishnode)
            expanded_nodes += 1
        return expanded_nodes,  len(path), path
    def is_solvable(self):
        state=self.state
        # Detemina si un estado es soluble, algunos no lo son por ejemplo https://www.youtube.com/watch?v=YI1WqYKHi78
        width = len(state[0])
        #Vemos si esta en el rango especificado
        if width!=len(state):
            raise NameError('Las dimensiones de la matriz no son validas, la matriz no es cuadrada')   
        if (width>10) or (width<3):
            raise NameError('Las dimensiones de la matriz no son validas, fuera del rango especificado')
        input_list=flatten(state)
        pos0=[(i,state[i].index(0))  if 0 in state[i] else None for i in range(width)]
        zero_location=next(item for item in pos0 if item is not None)        
        if zero_location[0] % 2 == 0: y_is_even = True
        else: y_is_even = False
        input_list = [number for number in input_list if number != 0]
        inversion_count = 0
        list_length = len(input_list)

        for index, value in enumerate(input_list):
            for value_to_compare in input_list[index + 1 : list_length]:
                if value > value_to_compare:
                    inversion_count += 1                    
        
        if inversion_count % 2 == 0: inversions_even = True
        else: inversions_even = False

        if width % 2 == 0: width_even = True
        else: width_even = False
        if width_even:
            zero_odd = not y_is_even
        return ((not width_even and inversions_even)
               or
               (width_even and (zero_odd == inversions_even)))
    def solvePuzzle(self):
        # Solucion del rompecabeza
        if not self.is_solvable():
            print('No es soluble se retorna None')
            return None
        n=len(self.state[0])
        flattened= flatten(self.state)
        goal = list(range(1, len(flattened)))+[0]
    #Checa que la matriz sea cuadrada
        if len(flattened) != n**2:
            steps, frontierSize, err = 0, 0, -1
        else:
            steps, frontierSize, solutions = self.Astar(self.state,self.state_cons(goal,n),self.Manhattan_distance)
            err = 0
        for i in solutions[1:]:
            t = PuzzleFrame(i)
            t.show()
            if i==self.state_cons(goal,n):
                print("Voila! Se resolvio el puzzle")
            else:
                print("EL Proximo paso es :")
    def state_cons(self,randomlist,n):
        matrix=[]
        r=0
        for i in range(0,n):
            matrix.append(randomlist[r:r+n])
            r+=n
        return matrix

if __name__ == "__main__":
    s = argv[1]
    state=[]
    for i in range(1,len(s.split('['))):
        state.append([int(j) for j in (s.split('[')[i].split(']')[0]).split(',')])
    PuzzleFrame(state).solvePuzzle()

    
