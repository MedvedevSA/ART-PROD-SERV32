import asyncio
from asyncio.events import set_event_loop
from AioFocasCNC import AioFocasCNC
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
import logging

from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(1)

_log_format = f"[%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

logging.basicConfig(
    #filename="MC.log",
    format=_log_format,
    level=logging.INFO
)



class MachineController(object):
    class CNC(object):
        def __init__(self) -> None:
            super().__init__()
            return

    def __init__(self):
        #threading.Thread.__init__(self)
        
        self.CNCSTATUS = dict()
        self.IP_LIST = [
            "192.168.1.28",
            "192.168.1.29",
            "192.168.1.30",
            "192.168.1.230",
            "192.168.1.231",
        ]
        self.data = dict()
        self.CNCOBJLIST = [AioFocasCNC(ip) for ip in self.IP_LIST]
        
        return 
        #self.initCNCList()
        #self.initCnc()
        #self.sch.add_job(self.getCncStatus, 'interval', seconds=3)
        #self.sch.start()
    def run(self):
        #Запуск асинхронного выполнения плановых задач
        asyncio.run(
            self.run_loop()
        )
        return

    async def run_loop(self):
        self.initCnc()

        while True:
            await asyncio.sleep(3)
            #logging.info('yap')
            #await self.aioMacro()
            
            await self.poolUpdStatusCnc()

    #def initCNCList(self):
        #for ip in self.IP_LIST:
            #self.CNCOBJLIST.append(
                #AioFocasCNC(ip)
            #)
        #return
    def getCncStatus(self):
        res = dict()
        for cnc in self.CNCOBJLIST:
            res[cnc._ip] = cnc._status
        return res

    def initCnc(self):
        self.CNCOBJLIST = list()
        t1 = time.time()
        for ip in self.IP_LIST:
            try:
                self.CNCOBJLIST.append(AioFocasCNC(ip))
            except:
                continue
        t2 = time.time()
        print('time',t2-t1)
        return

    async def readMacro (self, cnc:AioFocasCNC, number):
        loop = asyncio.get_event_loop()
        try:
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool,cnc.updLibh)
                res =  await loop.run_in_executor(pool,cnc.cnc_rdmacro, number)
                self.data.append(
                    res
                )
        except Exception as e:
            logging.info('except')


    async def aioMacro(self):
        cnc = self.CNCOBJLIST[3]
        tasks = list()
        for num in range(500,600):
            task = self.readMacro(cnc,num)
            tasks.append(task)

        await asyncio.gather(*tasks)
        

            

    async def addCncByIp(self, cnc : AioFocasCNC):
        pass
        #self.data.append(
            #await cnc.aioStart()
        #) 
        #try:
        #except Exception as e:
            #print(e)
            #pass

    async def connectCnc(self):
        t1 = time.time()
        tasks = list()
        for cnc in self.CNCOBJLIST:
            task = self.addCncByIp(cnc)
            tasks.append(task)

        await asyncio.gather(*tasks)
        t2 = time.time()
        print("Init async t2-t1" ,t2-t1)

    async def updStatusCnc(self, cnc : AioFocasCNC):
        #cnc.updLibh()
        loop = asyncio.get_event_loop()
        try:
            with ThreadPoolExecutor() as pool:
                res =  await loop.run_in_executor(pool,cnc.updStatus)
                self.data[cnc._ip] = res
        except:
            logging.info('except')
            self.CNCOBJLIST.remove(cnc)
        #self.data.append(
            #await cnc.aio_cnc_statinfo()
            ##cnc.cnc_statinfo()
        #)
        return

    async def poolUpdStatusCnc (self):
        t1 = time.time()
        tasks = list()
        for cnc in self.CNCOBJLIST:
            task = self.updStatusCnc(cnc)
            tasks.append(task)

        await asyncio.gather(*tasks)
        t2 = time.time()
        print("TaskList async t2-t1" ,t2-t1)
        return

    #def getCncStatus(self):

        #t1 = time.time()
        #for cnc in self.CNCOBJLIST:
            #t1 = time.time()
            #cnc.updLibh()
            #t2 = time.time()
            #print("t2-t1",t2-t1)
            #print(cnc.cnc_statinfo())
        '''
        for cnc in self.CNCOBJLIST:
            print(cnc.cnc_statinfo())
        for index in range(len(self.CNCOBJLIST)):
            try:
                res = self.CNCOBJLIST[index].cnc_statinfo()
                self.CNCSTATUS[self.CNCOBJLIST[index].init["ip"]] = res
            except:
                self.CNCSTATUS[self.CNCOBJLIST[index].init["ip"]] = None
                #CNCSTATUS[ip] = None
                #print(f"cnc : {ip} not found")
                print("fuck")
        '''
        t3 = time.time()
        print('time ', t2-t1)
        return  #{"item_id": cnc_id, "q": q}