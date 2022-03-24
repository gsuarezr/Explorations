puntos = 10;

mapa={'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9}

def totalPatternFromCur(visit, vecinos, cur, toTouch):
    if (toTouch <= 0):
         
        # if last cell then return 1 way
        if (toTouch == 0):
            return 1;
        else:
            return 0;
 
    ways = 0;
 
    # make this cell visited before
    # going to next call
    visit[cur] = True;
 
    for i in range(1, puntos):
 
        '''
        * if this cell is not visit AND either i and cur are adjacent (then
        * vecinos[i][cur] = 0) or between cell must be visit already ( then
        * visit[vecinos[i][cur]] = 1)
        '''
        if (visit[i] == False and (vecinos[i][cur] == 0 or visit[vecinos[i][cur]])):
            ways += totalPatternFromCur(visit, vecinos, i, toTouch - 1);
 
    # make this cell not visited
    # after returning from call
    visit[cur] = False;
 
    return ways;
 
# method returns number of pattern with
# minimum m connection and maximum n connection
def waysOfConnection(inicio,m):
    inicial=mapa[inicio]
    vecinos = [[0 for i in range(puntos)] for j in range(puntos)];
 
    # 2 lies between 1 and 3
    vecinos[1][3] = vecinos[3][1] = 2;
 
    # 8 lies between 7 and 9
    vecinos[7][9] = vecinos[9][7] = 8;
 
    # 4 lies between 1 and 7
    vecinos[1][7] = vecinos[7][1] = 4;
 
    # 6 lies between 3 and 9
    vecinos[3][9] = vecinos[9][3] = 6;
 
    # 5 lies between 1, 9 2, 8 3, 7 and 4, 6
    vecinos[1][9] = vecinos[9][1] = vecinos[2][8] = vecinos[8][2] =vecinos[3][7] = vecinos[7][3] = vecinos[4][6] = vecinos[6][4] = 5;
 
    visit = [False]*puntos;
    ways = 0;         
    tipo1=[1,3,7,9]
    tipo2=[2,4,6,8]
    if inicial in tipo1:
        ways += totalPatternFromCur(visit, vecinos, 1, m - 1);
    elif inicial in tipo2:
        ways +=  totalPatternFromCur(visit, vecinos, 2, m - 1);
    else:
        ways += totalPatternFromCur(visit, vecinos, 5, m - 1);
 
    return ways;
 
# Driver Code
if __name__ == '__main__':
    print("Indique el numero maximo de Conexiones:")
    maxConnect = int(input());
    print("Indique el nodo inicial")
    inicio=input()
 
    print(waysOfConnection(inicio,maxConnect));