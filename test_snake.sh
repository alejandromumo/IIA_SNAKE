#!/bin/bash


n=20 # Num jogos

## 20 FPS ##


#Default Map
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --vinte
done
# Mapa1 
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --vinte -m mapa1.bmp
done

# Mapa 2
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --vinte -m mapa2.bmp
done

# Mapa 3
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --vinte -m mapa3.bmp
done
# Mapa Qualify
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --vinte -m qualify1.bmp
done

## 30 FPS ##

#Default Map
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --trinta
done
# Mapa1 
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --trinta -m mapa1.bmp
done

# Mapa 2
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --trinta -m mapa2.bmp
done

# Mapa 3
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --trinta -m mapa3.bmp
done
# Mapa Qualify
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --trinta -m qualify1.bmp
done



## 40 FPS ##

#Default Map
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --quarenta
done
# Mapa1 
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --quarenta -m mapa1.bmp
done

# Mapa 2
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --quarenta -m mapa2.bmp
done

# Mapa 3
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --quarenta -m mapa3.bmp
done
# Mapa Qualify
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --quarenta -m qualify1.bmp
done



## 50 FPS ##

#Default Map
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --cinquenta
done
# Mapa1 
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --cinquenta -m mapa1.bmp
done

# Mapa 2
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --cinquenta -m mapa2.bmp
done

# Mapa 3
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --cinquenta -m mapa3.bmp
done
# Mapa Qualify
for i in $(seq 1 $n)
do
    py3.5 start.py -s Student,student -o Agent1,agent1 --disable-video --cinquenta -m qualify1.bmp
done

