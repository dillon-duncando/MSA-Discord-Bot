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
        if(round(n**(1/exponent), 2) % 1 == 0):
            return True
        exponent = exponent + 1
    return False

#naive prime detection algorithm    
def isPrime(x):
    #check if x is less than 2
    if(x < 2):
        return False
    #check if x is a perfect power
    if(isPerfectPower(x)):
        return False
    #continue with naive algorithm
    primes = primeFromList()
    hypothesis = True
    p = next(primes)
    while(hypothesis and p <= math.sqrt(x)):
        hypothesis = (x%p != 0)
        if(hypothesis):
            p = next(primes)
    return hypothesis
