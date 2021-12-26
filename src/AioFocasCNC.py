import ctypes
import os
import csv
import asyncio
#from time import time, sleep
import time
import logging

#from main import start_controller


class statinfo_ODBST(ctypes.Structure):
    _fields_ = [    ("hdck", ctypes.c_short) ,                   #/* Status of manual handle re-trace */
                    ("tmmode", ctypes.c_short) ,                 #/* T/M mode selection              */
                    ("aut", ctypes.c_short) ,                    #/* AUTOMATIC/MANUAL mode selection */
                    ("run", ctypes.c_short) ,                    #/* Status of automatic operation   */
                    ("motion", ctypes.c_short) ,                 #/* Status of axis movement,dwell   */
                    ("mstb", ctypes.c_short) ,                   #/* Status of M,S,T,B function      */
                    ("emergency", ctypes.c_short) ,              #/* Status of emergency             */
                    ("alarm", ctypes.c_short) ,                  #/* Status of alarm                 */
                    ("edit", ctypes.c_short) ]                   #/* Status of program editing       */

class ODBM(ctypes.Structure):
    _fields_ = [    ("datano"  , ctypes.c_short),           #/* custom macro variable number */
                    ("dummy"   , ctypes.c_short),           #/* (not used) */
                    ("mcr_val" , ctypes.c_long) ,           #/* value of custom macro variable */
                    ("dec_val" , ctypes.c_short) ]          #/* number of places of decimals */


#Подключение Lib
libpath = os.getcwd()
libpath = os.path.join(libpath,"Focas","Fwlib32.dll")
focas = ctypes.cdll.LoadLibrary(libpath)



class ListToolOffs ():
    class _2axis ():
        def __init__(self,x_Registry,z_Registry):

            self.__x_Registry = x_Registry
            self.__z_Registry = z_Registry

            self.X =[]
            self.Z =[]


        def get_x_Registry (self):
            return self.__x_Registry
            
        def get_z_Registry (self):
            return self.__z_Registry             

    def __init__(self,axis):
        if axis == 2:
            self.Wear = self._2axis(2000,2100)
            self.Geom = self._2axis(2700,2800)
        else :
            raise ValueError("Поддерживается только 2 оси")


class AioFocasCNC ():
    def __init__(self, ip):
        
        init = {
            "ip" : ip,
            "port" : 8193,
            "timeout" : 3,
            "libh" : ctypes.c_ushort(0)
        }
        self._ip = ip
        self._port  = 8193
        self._timeout  = 3
        self._libh = ctypes.c_ushort(0)

        self._status = {}

        self.init = init


    def updStatus(self):
        self.updLibh()
        self._status = self.cnc_statinfo()

        return self._status
        #self.start()
        #res = self.cnc_statinfo()
        
        #self.ToolOffs = ListToolOffs(axis=2)

        #self.ToolOffs_save(2)
        #self.ToolOffs.Wear.Z
        
    #def __del__ (self):
        #self.cnc_exit()
        #print('Succesful disconnect ip:{}'.format(self.init['ip']))
    
    #def cnc_exit(self):
        #ret = focas.cnc_freelibhndl(self.init["libh"])
        #if ret != 0:
            #raise Exception(f"Failed to free library handle! ({ret}) ip:{self.init['ip']}")
    
    def get_addr(self):
        return self.init["ip"]
    
    def ToolOffs_save (self,path):
        self.cnc_setpath(path)
        for i in range(1,100):
            self.ToolOffs.Wear.X.append(
                self.cnc_rdmacro( ctypes.c_short(self.ToolOffs.Wear.get_x_Registry() + i ) )
            )
            
            self.ToolOffs.Wear.Z.append(
                self.cnc_rdmacro( ctypes.c_short(self.ToolOffs.Wear.get_z_Registry() + i ) )
            )
            self.ToolOffs.Geom.X.append(
                self.cnc_rdmacro( ctypes.c_short(self.ToolOffs.Geom.get_x_Registry() + i ) )
            )
            
            self.ToolOffs.Geom.Z.append(
                self.cnc_rdmacro( ctypes.c_short(self.ToolOffs.Geom.get_z_Registry() + i ) )
            )
        table = [   self.ToolOffs.Geom.X,
                    self.ToolOffs.Geom.Z,
                    self.ToolOffs.Wear.X,
                    self.ToolOffs.Wear.Z]
        #транспонирование массива к виду таблицы
        table = list(map(list, zip(*table)))

        f_name = 'ToolOffs_{}_path-{}.csv'.format(
            self.init["ip"],
            path
        )
        
        with open(f_name, 'w', newline='') as f:
            write = csv.writer(f, delimiter =';',quoting=csv.QUOTE_MINIMAL)
            
            write.writerows(table)



    def updLibh (self):
        #Выделяет дескриптор библиотеки и подключается к ЧПУ с указанным IP-адресом или именем хоста
        #print("")
        #print("connecting to machine at {}:{}...".format(self.init["ip"], self.init["port"] ))
        
        ret = focas.cnc_allclibhndl3(
            self._ip.encode(),
            self._port,
            self._timeout,
            ctypes.pointer(self._libh),
        )
        
        if ret != 0:
            raise Exception(f"Failed to connect to cnc! ({ret})")

        try:
            cnc_ids = (ctypes.c_uint32 * 4)()
            ret = focas.cnc_rdcncid(self.init["libh"], cnc_ids)
            if ret != 0:
                raise Exception(f"Failed to read cnc id! ({ret})")

            machine_id = "-".join([f"{cnc_ids[i]:08x}" for i in range(4)])
            #print(f"machine_id={machine_id}\n")
        
        except:
            pass

    def cnc_statinfo(self):
        statinfo = statinfo_ODBST()
        #sleep(2)
        res = focas.cnc_statinfo(self._libh ,ctypes.byref(statinfo))
        res = dict()

        for field_name, dtype in statinfo._fields_:
            res[field_name] = getattr(statinfo,field_name)
            

        return res

    def cnc_setpath(self,n):
        focas.cnc_setpath(self.init["libh"],ctypes.c_short(n))


    def cnc_rdmacro (self, number, lenght=10):
        
        macro = ODBM()

        res = focas.cnc_rdmacro(  
            self.init["libh"],
            number,
            lenght,
            ctypes.byref(macro)
        )
        try :
            macro_val = macro.mcr_val/pow(10,macro.dec_val)
            #print ("Variable #{}={}".format(number,macro_val))
            
            return macro_val

        except ZeroDivisionError:
            return 0

#def main ():
#
#    init1 = {
#        "ip" : "192.168.1.28",
#        "port" : 8193,
#        "timeout" : 10,
#        "libh" : ctypes.c_ushort(0)
#    }
#
#    init2 = {
#        "ip" : "192.168.1.29",
#        "port" : 8193,
#        "timeout" : 10,
#        "libh" : ctypes.c_ushort(0)
#    }
#
#    init3 = {
#        "ip" : "192.168.1.30",
#        "port" : 8193,
#        "timeout" : 10,
#        "libh" : ctypes.c_ushort(0)
#    }
#
#    machine1 = FocasCNC(init1)
#    #machine2 = FocasCNC(init2)
#    #machine3 = FocasCNC(init3)
#
#
#if __name__ == '__main__':
#    main()