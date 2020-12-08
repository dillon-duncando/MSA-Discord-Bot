import discord
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import re, os, sys, math, time
from configparser import *
import pickle
import botFunctions as bf
from pnglatex import pnglatex

config = ConfigParser()
config.read('config.ini')

with open ('primelist', 'rb') as fp:
    primelist = pickle.load(fp)
    
def primeFromList():
    for prime in primelist:
        yield prime

#used to stop the bot from running a calculation that goes on for too long
class Timer:

    def __init__(self):

        self._start_time = None


    def start(self):

        """Start a new timer"""

        if self._start_time is not None:

            raise TimerError(f"Timer is running. Use .stop() to stop it")


        self._start_time = time.perf_counter()
        
        
    def time(self):
    
        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")
           
        elapsed_time = time.perf_counter() - self._start_time
        
        return(elapsed_time)


    def stop(self):

        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")


        elapsed_time = time.perf_counter() - self._start_time

        self._start_time = None

        print(f"Elapsed time: {elapsed_time:0.4f} seconds")

#an allow list for what functions can be called when plotting to avoid arbitrary code execution
safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees',
             'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp',
             'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh',
             'sqrt', 'tan', 'tanh']
             
safe_dict = {
    "sin"     : np.sin,
    "cos"     : np.cos,
    "tan"     : np.tan,
    "arcsin"  : np.arcsin,
    "arccos"  : np.arccos,
    "arctan"  : np.arctan,
    "sinh"    : np.sinh,
    "cosh"    : np.cosh,
    "tanh"    : np.tanh,
    "arcsinh" : np.arcsinh,
    "arccosh" : np.arccosh,
    "arctanh" : np.arctanh,
    "floor"   : np.floor,
    "ceil"    : np.ceil,
    "ln"      : np.log,
    "log"     : np.log10,
    "sinc"    : np.sinc,
    "sqrt"    : np.sqrt,
    "pi"      : math.pi,
    "tau"     : 2*math.pi,
    "e"       : np.exp(1)
}

#declare discord client
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #ignore messages from oneself
    if message.author == client.user:
        return

    #Hello world for discord
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        
    #return list of commands to give the bot
    if(message.content.startswith('$commands') or message.content.startswith('$help')):
        await message.channel.send(
        'List of commands: \n'\
        '$commands: Provide a list of commands \n'\
        '$factor x: Factor a positive integer x \n'\
        '$isPrime x: Check if integer x is prime \n'\
        '$plot f(x), min, max: Plot a function of x from the min to the max \n'\
        '$polar f(x), min, max: Plot a function of x from the min to the max in polar coordinates \n'\
        '$roll xdy: Roll x number of y sided dice \n'\
        '$tex or $Tex LaTeX: Render LaTeX code and return as an image'
        )
        
    #roll dice, like in d&d
    if message.content.startswith('$roll '):
        text = message.content[6:]
        index = text.find("d")
        if(index >= 0):
            await message.channel.send(bf.roll(text, index))
                
    #draw a 2d graph in cartesian coordinates
    #only uses arithmetic and functions defined in the safe dict
    if message.content.startswith('$plot '):
        text = message.content[5:]
        try:
            split = re.split(",", text.replace("^", "**"), 2)
            x = np.linspace(float(split[1]),float(split[2]), 100)
            y = eval(split[0], {**safe_dict, 'x': x})
            fig = plt.figure()
            plot = plt.plot(x,y)
            fig.savefig("newplot.png")
            await message.channel.send(file=discord.File("newplot.png"))
        except Exception as e:
            print(e)
            await message.channel.send('beep boop. something went wrong.')
            
    #draw a 2d graph in polar coordinates
    #only uses arithmetic and functions defined in the safe dict
    if message.content.startswith('$polar '):
        text = message.content[6:]
        try:
            split = re.split(",", text.replace("^", "**"), 2)
            x = np.linspace(float(split[1]),float(split[2]), 100)
            
            
            y = eval(split[0], {**safe_dict, 'x': x})
            fig = plt.figure()
            plot = plt.polar(x,y)
            fig.savefig("newplot.png")
            await message.channel.send(file=discord.File("newplot.png"))
        except Exception as e:
            await message.channel.send('beep boop. something went wrong.')
            await message.channel.send(e)
            
    #render latex
    if('$tex ' in message.content):
        command = message.content[(message.content.find('$tex ')+4):]
        try:
            sp.preview(command, viewer='file', filename='latex.png', euler=False)
            await message.channel.send(file=discord.File("latex.png"))
        except Exception as e:
            await message.channel.send('beep boop. something went wrong.')
            await message.channel.send(e)
            
    #render latex
    if('$Tex ' in message.content):
        command = message.content[(message.content.find('$Tex ')+4):]
        print(command)
        try:
            sp.preview(command, viewer='file', filename='latex.png', euler=False)
            await message.channel.send(file=discord.File("latex.png"))
        except Exception as e:
            print(e)
            await message.channel.send('beep boop. something went wrong.')
            
    #determine if a number is prime
    if message.content.startswith('$isPrime '):
        text = message.content[9:]
        try:
            x = int(text)
            if(bf.isPrime(x)):
                await message.channel.send(str(x) + ' is prime.')
            else:
                await message.channel.send(str(x) + ' is not prime.')
        except Exception as e:
            await message.channel.send('beep boop. something went wrong.')
            await message.channel.send(e)
    
    #factor a composite number, if possible within a reasonable amount of time
    if message.content.startswith('$factor '):
        text = message.content[8:]
        try:
            x = int(text)
            if(x <= 0):
                await message.channel.send("I don't know how to factor that.")
            elif(x == 1):
                await message.channel.send('1 = 1^1')
            elif(bf.isPrime(x)):
                await message.channel.send(str(x) + ' is a prime number.')
            else:
                factors = []
                exponents = []
                primes = primeFromList()
                index = 0
                timer = Timer()
                timer.start()
                time = timer.time()
                pFactor = bf.powerFactor(x)
                x = pFactor[0]
                expIncrement = pFactor[1]
                #jexpIncrement = 1
                while not bf.isPrime(x) and x != 1 and time < 60:
                    try:
                        p = next(primes)
                        if(x%p == 0):
                            factors.append(p)
                            exponents.append(0)
                            while(x%p == 0):
                                exponents[index] = exponents[index] + expIncrement
                                x = x//p
                            index = index + 1
                        if(math.sqrt(x) == math.floor(math.sqrt(x))):
                            x = math.floor(math.sqrt(x))
                            expIncrement = expIncrement * 2
                    except Exception as e:
                        message.channel.send(e)
                        factors.append(x)
                        exponents.append(1)
                        x = x//x
                    time = timer.time()
                timer.stop()
                if(bf.isPrime(x)):
                    factors.append(x)
                    exponents.append(expIncrement)
                factorization = []
                for i in range(len(factors)):
                    factorization.append(str(factors[i]) + "^" + str(exponents[i]))
                
                if time >= 60:
                    await message.channel.send("Computation took too long.")
                    msg = str(int(text)) + ' = ' + "+".join(factorization) + " + a potential prime or semiprime " + str(x)
                else:   
                    msg = str(int(text)) + ' = ' + "+".join(factorization)
                await message.channel.send(msg)
        except Exception as e:
            print(e)
            await message.channel.send('beep boop. something went wrong.')
            
    #returns pi in terms of the superior circle constant
    if message.content.startswith('$pi'):
        await message.channel.send('π = τ/2')
        
    #restart the bot, mostly useful to update the code of the bot
    #it should open itself, then close itself, but sometimes it just opens itself.
    if message.content.startswith('$restart'):
        #check the message author is authorized to restart the bot
        if message.author.name == config.get("main", "owner"):
            await message.channel.send('brb')
            os.startfile(__file__)
            sys.exit()
    
    #shut down the bot
    if message.content.startswith('$shutdown'):
        #check the message author is authorized to shut down the bot
        if message.author.name == config.get("main", "owner"):
            await message.channel.send('Goodbye.')
            print("Terminating bot")
            sys.exit()
 
#config is in the git ignore to avoid publishing the bot id in a public repository 
#the bot id can be acquired by creating a bot application at https://discord.com/developers/applications
client.run(config.get("main", "id"))
