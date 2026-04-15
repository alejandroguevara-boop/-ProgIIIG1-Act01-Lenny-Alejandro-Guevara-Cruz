%EJERCICIO 1 POR MEDIO DE ESTRUCTURAS, LISTAS Y RECURSIVIDAD:

% Lista de relaciones padre-hijo
padres([
    papa(abraham,herbert),   
    papa(abraham,homero),    
    papa(clancy,marge),     
    papa(clancy,patty),      
    papa(clancy,selma),      
    papa(homero,bart),       
    papa(homero,lisa),      
    papa(homero,maggie)      
]).

% Lista de relaciones madre-hijo
madres([
    mama(mona,herbert),      
    mama(mona,homero),       
    mama(jacqueline,marge),  
    mama(jacqueline,patty),  
    mama(jacqueline,selma),  
    mama(marge,bart),        
    mama(marge,lisa),       
    mama(marge,maggie),    
    mama(selma,ling)        
]).

% BÚSQUEDA EN LISTAS

% Caso 1: Se encuentra una relación padre-hijo al inicio de la lista
buscar(X,Y,[papa(X,Y)|_]).

% Caso 2: Se encuentra una relación madre-hijo al inicio de la lista
buscar(X,Y,[mama(X,Y)|_]).

% Caso 3: Si no está al inicio, se sigue buscando en la cola de la lista
buscar(X,Y,[_|T]) :-
    buscar(X,Y,T).

% RELACIÓN ACUDIENTE (PADRE O MADRE)

% X es acudiente de Y si X aparece como padre de Y
acudiente(X,Y) :-
    padres(L),
    buscar(X,Y,L).

% X es acudiente de Y si X aparece como madre de Y
acudiente(X,Y) :-
    madres(L),
    buscar(X,Y,L).

% RELACIONES FAMILIARES

% Abuelo: X es abuelo de Y si X es acudiente de Z y Z es acudiente de Y
abuelo(X,Y) :-
    acudiente(X,Z),
    acudiente(Z,Y).

% Nieto: X es nieto de Y si Y es abuelo de X
nieto(X,Y) :-
    abuelo(Y,X).

% Hermano: X y Y son hermanos si comparten al menos un acudiente
% y no son la misma persona
hermano(X,Y) :-
    acudiente(P,X),
    acudiente(P,Y),
    X \= Y.

% Tío: X es tío de Y si X es hermano de un acudiente de Y
tio(X,Y) :-
    hermano(X,Z),
    acudiente(Z,Y).

% Sobrino: relación inversa de tío
sobrino(X,Y) :-
    tio(Y,X).

% Hijo: X es hijo de Y si Y es acudiente de X
hijo(X,Y) :-
    acudiente(Y,X).

% Primo: X es primo de Y si el acudiente de X es tío de Y
primo(X,Y) :-
    acudiente(Z,X),
    tio(Z,Y).

% EJEMPLOS DE CONSULTA
% ¿Abraham es abuelo de Bart?
% ?- abuelo(abraham, bart).

% ¿Bart y Lisa son hermanos?
% ?- hermano(bart, lisa).

% ¿Herbert es tío de Bart?
% ?- tio(herbert, bart).

% ¿Bart es primo de Ling?
% ?- primo(bart, ling).

-------------------------------------------------------------------------------------------------------------------------

%EJERCICIO 2 POR MEDIO DE ESTRUCTURAS, LISTAS Y RECURSIVIDAD:

%HECHOS

ruta(ciudad(edmonton), 
     [destino(ciudad(saskatoon), costo(12))]).

ruta(ciudad(saskatoon), 
     [destino(ciudad(winniepeg), costo(20)),
      destino(ciudad(calgary), costo(9))]).

ruta(ciudad(regina), 
     [destino(ciudad(saskatoon), costo(7)),
      destino(ciudad(winniepeg), costo(4))]).

ruta(ciudad(calgary), 
     [destino(ciudad(regina), costo(14)),
      destino(ciudad(edmonton), costo(4))]).

ruta(ciudad(vancouver), 
     [destino(ciudad(edmonton), costo(16)),
      destino(ciudad(calgary), costo(13))]).

%REGLAS

% Nodo tiene aristas
aristas(X):-  
    ruta(ciudad(X),_), !; 
    ruta(_, Lista), member(destino(ciudad(X), _), Lista).

% Conexión directa
hay_ruta_directa(Origen, Destino, Costo):-  
    ruta(ciudad(Origen), Lista), 
    member(destino(ciudad(Destino), costo(Costo)), Lista).

viaje(Origen, Destino, Costo):-        
    hay_ruta(Origen, Destino, [Origen], Costo).

% Caso base
hay_ruta(Origen, Destino, _, Costo):-  
    ruta(ciudad(Origen), Lista), 
    member(destino(ciudad(Destino), costo(Costo)), Lista).


% Caso recursivo con lista de visitados (CLAVE)
hay_ruta(Origen , Destino, Visitados, Costo):- 
    ruta(ciudad(Origen), Lista), 
    member(destino(ciudad(Intermedio), costo(Costo_1)), Lista), 
    \+ member(Intermedio, Visitados),  % evita ciclos reales
    hay_ruta(Intermedio, Destino, [Intermedio|Visitados], Costo_2), 
    Costo is Costo_1 + Costo_2.

%EJEMPLOS DE CONSULTA:
%?- hay_ruta_directa(regina, winniepeg, C).
%C = 4.

%?- aristas(winniepeg).
%true.

%?- viaje(vancouver, winniepeg, C).
%C = 48.

%?- viaje(calgary, saskatoon, C).
%C = 21.

%?- viaje(edmonton, calgary, _).
%true.
