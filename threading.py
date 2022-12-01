"""
* Wilhelm Groth
* Threading laboration 4
* 2021-05-01
* thread.py
"""

import time
from datetime import datetime
from threading import Thread
from threading import Lock

            
# Lite lås
mlock = Lock()    # Skyddar "m"
lockcount = Lock() # Skyddar counter
writerpriolock = Lock() # Ska ge prio till skrivare
lockwrite = Lock() # Skyddar writercounter




# datum https://www.programiz.com/python-programming/datetime/strftime
now = datetime.now()
date_time = now.strftime("%Y/%m/%d, %H:%M:%S: %f")
date_time_reverse = now.strftime("%f:%S:%M:%H, %d/%m/%Y")


# Lite variabler
m = date_time
counter = 0
writercounter = 0 

class Läsare(Thread):
    def run(self):
        while True: # Körs till manuellt stopp (ctrl+z)
            global m
            global counter

            # Entry
            writerpriolock.acquire() # Detta lås används för att kolla om den kan gå vidare eller ej (Om en skrivare används för tillfället)
            writerpriolock.release() 
            lockcount.acquire()
            counter += 1
            if (counter == 1):
                mlock.acquire()  # Första läsaren tar låset för "m" och alla andra läsare hoppar över 
            lockcount.release()

            # Kritiska
            print("--------------------------------")
            print(self.name, " | ", m)
            print("--------------------------------")

            # Exit
            lockcount.acquire()
            counter -= 1
            if (counter == 0):
                mlock.release()     # Sista läsaren släpper ifrån sig låset för "m" och ger skrivarna möjligthet att skriva till
            lockcount.release()

class Skrivare(Thread):
    def run(self):
        while True: # Körs till manuellt stopp (ctrl+z)
            global m
            global now
            global date_time
            global writercounter

            # Entry
            lockwrite.acquire()
            writercounter += 1
            if (writercounter == 1): # Gör så att inte två skrivare kan skriva smamtidigt 
                writerpriolock.acquire() # Skrivaren håller på priolock för att få prioritet
            lockwrite.release()
            mlock.acquire() # Får låset för att kunna ändra datumstämpeln

            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d (%H:%M:%S: %f)       | ORIGINAL ") 
            m = date_time   # Skriver till m/resursen
            mlock.release() # Släpper på låset för kritiska/m 

            lockwrite.acquire()
            writercounter -= 1
            if (writercounter == 0):
                writerpriolock.release() # Släpper på priolocket så andra skrivare/läsare kan få tillgång
            lockwrite.release()

class reversewriter(Thread):
    def run(self):
        while True: # Körs till manuellt stopp (ctrl+z)
            global m
            global now
            global date_time
            global writercounter
            
            # Entry
            lockwrite.acquire()
            writercounter += 1
            if (writercounter == 1): 
                writerpriolock.acquire()  
            lockwrite.release()
                
            
            mlock.acquire()  # Skyddar kritiska/variabeln m
            now = datetime.now()
            date_time_reverse = now.strftime("(%f:%S:%M:%H) %d-%m-%Y     | REVERSE ")
            m = date_time_reverse 
            mlock.release() # Släpper på låset 
            
           # Exit
            lockwrite.acquire()
            writercounter -= 1
            if (writercounter == 0):
                writerpriolock.release()  
            lockwrite.release()
            
 
def start():
    print("START TID = ", date_time)
    #http://apachepersonal.miun.se/~jimahl/DT011G/one_lock_at_a_time.py

    # AKTÖRER

    #Skriver ut en datumstämpel, inkl sekunder till textsträngen
    s1 = Skrivare()
    s1.daemon = True # bakgrundstrådar 
    s1.start()

    #Skriver en omvänd datumstämpel. inkl sekunder till textsträngen
    sr = reversewriter()
    sr.daemon = True
    sr.start()

    #Läsare 1   Läser och skriver ut textsträngen till standarduströmmen.
    läs1 = Läsare()
    läs1.daemon = True
    läs1.start()

    #Läsare 2
    läs2 = Läsare()
    läs2.daemon = True
    läs2.start()

    #Läsare 3
    läs3 = Läsare()
    läs3.daemon = True
    läs3.start()
    
    threads = [s1, sr, läs1, läs2, läs3]
    for t in threads:
        t.join()


start() 

