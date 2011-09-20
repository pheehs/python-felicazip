#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
from ctypes import *
from ctypes.wintypes import HINSTANCE
flib = cdll.felicalib

POLLING_ANY = 0xFFFF
POLLING_SUICA = 0x0003
POLLING_EDY = 0xFE00


class PASORI(Structure):
    _field_ = [
        ("hInstDLL", HINSTANCE),
        ]

class FELICA(Structure):
    _field_ = [
        ("p", PASORI),
        ("systemcode", c_uint16),
        ("IDm", c_uint8),
        ("PMm", c_uint8),
        ("num_system_code", c_uint8),
        ("system_code", c_uint16),
        ("num_area_code", c_uint8),
        ("area_code", c_uint16),
        ("end_service_code", c_uint16),
        ("num_service_code", c_uint8),
        ("service_code", c_uint16),
        ]

class PaSoRiReader(object):
    def __init__(self):
        self.pasori = None
        self.felica = None
        self.IDm = c_uint64()
        self.PMm = c_uint64()
        
        flib.pasori_open.restype = c_void_p
        flib.felica_polling.restype = c_void_p

        self.pasori = flib.pasori_open()
        flib.pasori_init(self.pasori)
        if not self.pasori:
            print "PaSoRi open error!"


    def open(self):
        self.felica = flib.felica_polling(self.pasori, POLLING_ANY, 0, 0)
        if not self.felica:
            return False
        else:
            return True
    
    def read(self):
        if not self.pasori:
            print "Please open PaSoRi."
            return False
        if not self.felica:
            print "Please poll Felica"
            return False
        flib.felica_getidm(self.felica, byref(self.IDm))
        flib.felica_getpmm(self.felica, byref(self.PMm))
        #print "IDM:0x%016X" % self.IDm.value
        #print "PMm:0x%016X" % self.PMm.value
        return self.IDm.value

    def close(self):
        flib.pasori_close(self.pasori)
        return 1

if __name__ == "__main__":
    ic = PaSoRiReader()
    ic.open()
    ic.read()
    ic.close()
