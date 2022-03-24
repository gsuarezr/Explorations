# Prueba_Open_Python
Este repo es la implementacion de los retos de python propuestos por OpenBootCamp


# Primer reto

Este reto se implemento en el algoritmo primero.py, toma como argumentos dos numeros el primero debe ser menor al segundo de lo contrario se levanta un error


## Ejemplos Primer Reto:

python primero.py 1 200
Tenemos 9 numeros invertidos validos, los cuales son 1, 8, 11, 69, 88, 96, 101, 111, 181

el print es solo estetico, la funcion retorna ([1, 8, 11, 69, 88, 96, 101, 111, 181], 9) como pide la documentacion del reto, una lista de todos los numeros strobograficos en el rango y la cantidad

python primero.py  200 1
Traceback (most recent call last):
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/primero.py", line 35, in <module>
    raise NameError('Se ingreso un numero no valido el primer numero debe ser menor al segundo')
NameError: Se ingreso un numero no valido el primer numero debe ser menor al segundo

  
# Se documenta primero el tercero porque los ejemplos del segundo son extensos
  
# Tercer Reto
  
El tercer reto esta implementado en el script tercero.py, toma como input la cantidad maxima de nodos en el patron y el nodo del cual inicia el patron, esta vez el input se pide una vez iniciado el programa
  
# Ejemplos Tercer Reto:
  
python tercero.py                                                                       
Indique el numero maximo de Conexiones:
2
Indique el nodo inicial
C
5

# Segundo Reto
El segundo reto se implemento en el script segundo.py, el input de este script es una matriz pasada como un string, se puede apreciar mejor el uso del script en los ejemplos, para la solucion se uso el algoritmo A* con la distancia de manhattan como funcion heuristica

## Ejemplos Segundo Reto:

python segundo.py "[1, 2, 3, 4], [5, 6, 8, 11], [9, 10, 7, 12], [13, 15, 14, 0]"
No es soluble se retorna None

La funcion retorna None ese print es para visualizacion

python segundo.py "[1, 2],[3,4]"                                                
Traceback (most recent call last):
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 167, in <module>
    PuzzleFrame(state).solvePuzzle()
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 135, in solvePuzzle
    if not self.is_solvable():
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 108, in is_solvable
    raise NameError('Las dimensiones de la matriz no son validas, fuera del rango especificado')
NameError: Las dimensiones de la matriz no son validas, fuera del rango especificado
 
 
 python segundo.py "[1, 2, 3, 4,4], [5, 6, 8, 11,4], [9, 10, 7, 12,4], [13, 15, 14, 0,4]"
Traceback (most recent call last):
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 167, in <module>
    PuzzleFrame(state).solvePuzzle()
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 135, in solvePuzzle
    if not self.is_solvable():
  File "/mnt/c/Users/gerar/OneDrive - University of Gdansk (for Students)/new/segundo.py", line 106, in is_solvable
    raise NameError('Las dimensiones de la matriz no son validas, la matriz no es cuadrada')   
NameError: Las dimensiones de la matriz no son validas, la matriz no es cuadrada
  
Para algunos ejemplos el algoritmo puede ser muy lento sin embargo sin falla encuentra la solucion, se intento usar el algoritmo de Dijkstra pero resulto ser mas lento al final:
  
new python segundo.py "[5, 13, 1, 15], [9, 0, 11, 8], [2, 7, 4, 12], [3, 6, 14, 10]"
  
----------------                                 
|5  |13 |1  |15 |
----------------
|9  |0  |11 |8  |
----------------
|2  |7  |4  |12 |       .............   
----------------
|3  |6  |14 |10 |
----------------
----------------
|1  |2  |3  |4  |
----------------
|5  |6  |7  |8  |
----------------
|9  |10 |11 |12 |
----------------
|13 |14 |15 |0  |
----------------
  
