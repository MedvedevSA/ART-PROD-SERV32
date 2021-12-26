from asyncio import tasks
from asyncio.events import new_event_loop
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional
from pydantic.tools import T
from starlette.responses import Response
import uvicorn

import asyncio
from MachineController import MachineController

#import threading

from fastapi import FastAPI , HTTPException
from fastapi_utils.tasks import repeat_every

from pydantic import BaseModel
import time


CNCSTATUS = dict()
IP_LIST = [
    "192.168.1.28",
    "192.168.1.29",
    "192.168.1.30",
    "192.168.1.230",
]

CNCOBJLIST = list()

app = FastAPI()
machineManager = MachineController()

"""
@app.get("/cnc/{cnc_id}")
def responseCncStatus(cnc_id: int, run: Optional[int] = None):

    t1 = time.time()
    cnc = custom_Focas.FocasCNC(IP_LIST[cnc_id-1])
    res = cnc.cnc_statinfo()
    print("time" , time.time() - t1)

    return res
"""

@app.get("/cnc/status/{cnc_id}")
def responseCncStatus(cnc_id: int, run: Optional[int] = None):
    return machineManager.CNCSTATUS[
        machineManager.IP_LIST[cnc_id-1]
    ]
    return CNCSTATUS[IP_LIST[cnc_id-1]]

@app.get("/get")
def read_root():
    response = machineManager.getCncStatus()  
    return response

@app.get("/")
def read_root():
    return {"Hello": "World"}

def test():
    print("lol")

def start_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000,log_level="info")

def start_controller():
    machineManager.run()
async def test():
    while True:
        s = '$!-'*40
        print(time.strftime('%X %x %Z')+s)
        await asyncio.sleep(1)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    #scheduler.add_job(thr)
    #scheduler.add_job(thread.getCncStatus, 'interval', seconds=3)
    scheduler.add_job(start_uvicorn)
    scheduler.add_job(start_controller)
    scheduler.add_job(test)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass