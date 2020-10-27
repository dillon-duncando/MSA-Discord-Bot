import discord
import matplotlib.pyplot as plt
import numpy as np
import re, os, sys, math, time
from configparser import *
import pickle

with open ('primelist', 'rb') as fp:
    primelist = pickle.load(fp)
    
def primeFromList():
    for prime in primelist:
        yield prime

#roll dice
def roll(text, index):
    try:
        left = int(text[:index])
        right = int(text[index+1:])
        if(left <= 0 or right <= 0):
            return "My dice disappeared. I don't have anything to roll."
        elif(left > 500):
            return "Sorry, I don't have that many dice."
        else:
            array = np.random.randint(0,right,left)
            newRoll = np.frombuffer(array, dtype=int)
            return newRoll
    except:
        return 'beep boop. something went wrong.'
        
def isPerfectPower(n):
    if(n < 1):
        return False
    exponent = 2
    while exponent <= math.log2(n):
        if(round(n**(1/exponent)) ** exponent == n):
            return True
        exponent = exponent + 1
    return False
    
#struggles with powers of mersenne primes due to floating point errors
def powerFactor(n):
    if(not isPerfectPower(n)):
        return(n, 1)
    else:
        testExp = 2
        while testExp <= math.log2(n):
            if(round(n**(1/testExp)) ** testExp == n):
                exponent = testExp
                break
            testExp = testExp + 1
        if(isPerfectPower(round(n**(1/exponent)))):
            factor = powerFactor(round(n**(1/exponent)))
            return(factor[0], factor[1] * exponent)
        else:
            return(round(n**(1/exponent)), exponent)
            
#step 2 in aks algorithm
def findMinr(n):
    for r in range(2,max(4,math.ceil(math.log2(n)**5)+1)):
        if(math.gcd(n,r) == 1):
            flag = True
            for k in range(1,math.ceil(math.log2(n)**2)):
                if(pow(n,k,r) == 1):
                    flag = False
                    break
            if(flag):
                return(r)

def isPrime(x):
    #check if x is less than 2
    if(x < 2):
        return False
    #check if x is a perfect power
    if(isPerfectPower(x)):
        return False
    #use primelist to detect small primes
    primes = primeFromList()
    hypothesis = True
    p = next(primes)
    #99999989 is the largest prime in the primelist.
    #using the naive algorithm with the saved list is faster than steps 2 to 6 of aks
    #but only so many prime numbers can be saved.
    while(hypothesis and p <= math.sqrt(x) and p < 99999989):
        hypothesis = (x%p != 0)
        if(hypothesis):
            p = next(primes)
    if not hypothesis or p < 99999989:
        return hypothesis
    else:
        #run steps 2 and 3 of aks
        r = findMinr(x)
        for i in range(r):
            if(1 < math.gcd(i,x) < x):
                return False
        #step 4 of aks
        if(r >= x):
            return True
        else:
            #the rest of aks will go here
            return hypothesis