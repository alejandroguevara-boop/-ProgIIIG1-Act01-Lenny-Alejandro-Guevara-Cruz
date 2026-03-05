% ACTIVIDAD # 2: BACTRACKING GRAFO DIRIGIDO

%    NODO---COSTO--->NODO
% edmonton---12--->saskatoon
% saskatoon--20--->winniepeg
% regina-----7---->saskatoon
% regina-----4---->winniepeg
% calgary----14--->regina
% calgary----4---->edmonton
% vancouver--16--->edmonton
% vancouver--13--->calgary
% saskatoon--9---->calgary

%---------------------- HECHOS -----------------------------
ruta(edmonton,saskatoon,12).
ruta(saskatoon,winniepeg,20).
ruta(regina,saskatoon,7).
ruta(regina,winniepeg,4).
ruta(calgary,regina,14).
ruta(calgary,edmonton,4).
ruta(vancouver,edmonton,16).
ruta(vancouver,calgary,13).
ruta(saskatoon,calgary,9).

%------------------------ REGLAS -----------------------------
aristas(X):- % Comprueba que una ciudad tenga aristas, ya sea de entrada o salida
    ruta(X,_,_), !;
    ruta(_,X,_).

hay_ruta_directa(Origen, Destino, Costo):- % Comprueba si hay una ruta directa entre 2 ciudades
    ruta(Origen, Destino, Costo).

% Regla recursiva
viaje(Origen, Destino, Costo):- % Comprueba si existe una ruta entre 2 ciudades pasando por otras ciudades
    hay_ruta(Origen, Destino, Origen, Costo). /* Se envia el origen para comparar ciudades intermedias
                                               * y no volver a pasar por el origen */

hay_ruta(Origen, Destino, _ ,Costo):-  % caso base: existe una ruta desde una ciudad a otra
  ruta(Origen, Destino, Costo).

hay_ruta(Origen , Destino, CiudadOrigen, Costo):- % Caso recursivo: Existe una ruta desde una ciudad a otra pasando por una ciudad intermedia
    ruta(Origen , Intermedio , Costo_1),
    Intermedio \= CiudadOrigen,  % Comprueba que la ciudad intermedio no sea la ciudad original, con el fin de evitar ciclos infinitos
    hay_ruta(Intermedio, Destino, CiudadOrigen ,Costo_2),
    Costo is Costo_1 + Costo_2,
    !.

%---------------------- CONSULTAS ---------------------------
% 1) Existe una conexión entre Saskatoon y Vancouver?
% ?- hay_ruta_directa(saskatoon, vancouver, _).
%       Respuesta esperada: False
%      
%     ?- hay_ruta_directa(regina, winniepeg, _).
%         Respuesta esperada: True

% 2) Con qué nodos está conectado Regina y cual es el costo de cada conexion?
% ?- hay_ruta_directa(regina, X , C).
%         Respuesta esperada:
% Resultado 1: C = 7
%     X = Saskatoon
%        
%        Resultado 2: C = 4
%     X = Winniepeg

% 3) Regla para determinar si un nodo tiene aristas:
% ?- aristas(vancouver).
% Respuesta esperada: True
%
%     ?- aristas(winniepeg).
% Respuesta esperada: True

% 4) Regla para determinar cual es el costo para ir de un nodo X a Z pasando por Y.
% ?- viaje(vancouver, winniepeg, C).
% Respuesta esperada: C = 48
%
% ?- viaje(calgary, saskatoon, C).
% Respuesta esperada: C = 21

% 5) Es posible viajar desde Edmonton a Calgary?
% ?- viaje(edmonton, calgary, _).
%         Respuesta esperada: True
