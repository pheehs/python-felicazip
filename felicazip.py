#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os.path
import optparse
import time
from felica import PaSoRiReader
from hashlib import sha256
from ctypes import *

lib7z = WinDLL("7-zip32.dll")

usage =  u"%prog (-e/-d/-c) INPUT_FILE [-o output file(directory)]"
version = u"%prog 0.1"

codec = sys.getfilesystemencoding()


def log(logstr):
    print logstr.encode(codec)
    return
    
def SevenZip(cmd):
    """
    //x=[0|1|3|5|7|9]
    #a {output name} {input file(s)} -t7z -p{password} -mhe -mx={level}
    #x {input file} -t7z -p{password}
    """
    log("\n"+u"*" * 50)
    lib7z.SevenZip.argtypes = [c_long, c_char_p, c_char_p, c_ulong]
    hwnd = c_long()
    resbuf = c_buffer(5000)
    res = lib7z.SevenZip(hwnd, cmd, resbuf, sizeof(resbuf))
    print resbuf.value[2:-2].replace("\r", "").replace("\n\n", "\n")
    log(u"*" * 50+"\n")
    if res != 0:
        return False
    else:
        return True

def Encrypt(inpath, outpath, passwd, level=5):
    cmd = 'a "%s" "%s" -t7z -p%s -mhe -mx=%d' \
        % (outpath, inpath, passwd, level)
    res = SevenZip(cmd)
    if res == True:
        log(u"暗号化完了！")
        return True
    else:
        log(u"暗号化失敗！")
        return False

def Decrypt(inpath, outpath, passwd):
    cmd = 'x "%s" -o"%s" -t7z -p%s' \
        % (inpath, outpath, passwd)
    res = SevenZip(cmd)
    if res == True:
        log(u"復号化完了！")
        return True
    else:
        log(u"復号化失敗！")
        return False
    
def CheckArchive(filepath, level=0):
    lib7z.SevenZipCheckArchive.argtypes = [c_char_p, c_int]
    res = lib7z.SevenZipCheckArchive(filepath, level)
    if res == False:
        log(u"暗号化されたファイルではありません。")
        return False
    else:
        log(u"正常に暗号化されたファイルです。")
        return True

def GetIDmSHA256():
    opening = False
    pr = PaSoRiReader()
    log(u"ICカードをタッチしてください。")
    while opening == False:
        opening = pr.open()
        time.sleep(1)
    log(u"ICカードが認識されました。")
    idm = pr.read()
    pr.close()
    if idm == False:
        return None
    #print "IDm:", idm
    h = sha256(str(idm)).hexdigest()
    log(u"パスワード: " + h)
    return h

def CallEncryption(inpath, outpath):
    passwd = GetIDmSHA256()
    if not outpath:
        res = Encrypt(inpath, inpath + ".fle", passwd)
    else:
        res = Encrypt(inpath, outpath, passwd)
    return

def CallDecryption(inpath, outpath):
    passwd = GetIDmSHA256()
    if not outpath:
        res = Decrypt(inpath, os.path.dirname(inpath), passwd)
    else:
        res = Decrypt(inpath, outpath, passwd)
    return

def main():
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-o", "--output",
                      action="store",
                      type="string",
                      help=u"暗号化ファイルの保存先/復号化後の保存先の指定",
                      )
    parser.add_option("-e", "--encryption",
                      action="store_true",
                      help=u"暗号化モードにする",
                      )
    parser.add_option("-d", "--decryption",
                      action="store_true",
                      help=u"復号化モードにする",
                      )
    parser.add_option("-c", "--check",
                      action="store_true",
                      help=u"正常な暗号化ファイルか判断する。",
                      )
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error("input file parameter is necessary")
    if options.encryption:
        CallEncryption(args[0], options.output)
    elif options.decryption:
        CallDecryption(args[0], options.output)
    elif options.check:
        CheckArchive(args[0])
    else:
        parser.error("show help to -h or --help option")
    
    return

if __name__ == "__main__":
    main()
