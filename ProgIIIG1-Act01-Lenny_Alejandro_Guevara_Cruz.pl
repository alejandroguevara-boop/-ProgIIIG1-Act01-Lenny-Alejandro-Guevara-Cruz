% EJERCICIO 1: 
% DIRECTAS:  
papa(abraham,herbert). 
papa(abraham, homero). 
papa(clancy,marge). 
papa(clancy,patty). 
papa(clancy, selma). 
papa(homero,bart). 
papa(homero,lisa). 
papa(homero,maggie). 
mama(mona,herbert). 
mama(mona, homero). 
mama(jacqueline, marge). 
mama(jacqueline,patty). 
mama(jacqueline,selma). 
mama(marge,bart). 
mama(marge,lisa). 
mama(marge,maggie). 
mama(selma,ling). 
% REGLAS: 
acudiente(X,Y):- papa(X,Y). 
acudiente(X,Y):-mama(X,Y). 
abuelo(X,Y):- acudiente(X,Z), acudiente(Z,Y). 
nieto(X,Y):-abuelo(Y,X). 
tio(X,Y):- hermano(X,Z), acudiente(Z,Y). 
sobrino(X,Y):-tio(Y,X). 
hijo(X,Y):- acudiente(Y,X). 
hermano(Z,Y):-acudiente(X,Y),acudiente(X,Z), Z\=Y. 
primo(X,Y):-acudiente(Z,X), tio(Z,Y). 
% Consultas: 
% abuelo(abraham,lisa). 
% nieto(bart,clancy). 
% hermano(bart,lisa). 
% hijo(lisa,homero). 
% tio(patty,maggie). 
% sobrino(maggie,selma). 
% primo(ling,bart). 
% acudiente(marge,bart). 
% tio(herbert,ling) 
% ->false 
% EJERCICIO 2: 
% HECHOS: 
estadounidense(west). 
nacion(corea_del_sur). 
hostil(corea_del_sur). 
misil(m1). 
posee(corea_del_sur, m1). 
vendio(west, m1, corea_del_sur). 
% REGLAS: 
arma(X) :- misil(X). 
criminal(X) :- 
estadounidense(X), 
vendio(X, Objeto, Pais), 
arma(Objeto), 
hostil(Pais). 
% Consulta: 
% criminal(west). 
% ->true
