import sys
import fnmatch
import os
import datetime
from collections import OrderedDict
import getopt
import re
from Canvas import Line
from __builtin__ import True

HEADER = re.compile("\s*FECHA\s*CONCEPTO\s*RETIROS\s*DEPOSITOS\s*SALDO")
# (?P<dia>[0-9]{2})\s*(?P<mes>[A-Z]{3})\s(?P<concepto>(?:(?:\S ?)*\n?))\s*(?P<monto>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?\s*(?P<saldo>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?
REGISTRO = "(?P<dia>[0-9]{2})\s*(?P<mes>[A-Z]{3})\s(?P<concepto>(?:\S ?)*)\s*(?P<monto>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?\s*(?P<saldo>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?"
REGISTROML = "\s*(?P<concepto>(?:\S ?)*)\s*(?P<monto>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?\s*(?P<saldo>[0-9]{1,3}(?:,?[0-9]{3})*\.[0-9]{2})?"
REGREG = re.compile(REGISTRO)
REGREGML = re.compile(REGISTROML)

class EstadoDeCuenta:
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        inreg = False
        dia = ''
        mes = ''
        concepto = ''
        monto = ''
        saldo = ''
        for line in open(self.filename):
            #print line
            if inreg:
                if REGREGML.match(line):
                    m = REGREGML.search(line)
                    _concepto = m.group('concepto')
                    _monto = m.group('monto')
                    _saldo = m.group('saldo')
                    concepto =  concepto + ' ' +_concepto
                    if _monto != None:
                        monto = _monto
                        saldo = _saldo
                        inreg = False
                        print "%s %s %-180s $%s         $%s"%(dia, mes, concepto, monto, saldo)
                else:
                    print Line
                    inreg = False
            
            elif REGREG.match(line):
                m = REGREG.search(line)
                _dia = m.group('dia') 
                _mes = m.group('mes')
                _concepto = m.group('concepto')
                _monto = m.group('monto')
                _saldo = m.group('saldo')
                #print "%s %s %s $%s         $%s"%(_dia, _mes, _concepto, _monto, _saldo)
                dia = _dia
                mes = _mes
                concepto = _concepto
                monto = _monto
                saldo = _saldo
                if _monto == None:
                    inreg = True
                else:
                    print "%s %s %-180s $%s         $%s"%(dia, mes, concepto, monto, saldo)
            
        

class EstadosDeCuenta:
    def __init__(self):
        self.edcs = []
        self.recursive = False
        
    def usage(self):
        print "Parse"
    
    def parse_args(self,argv):
        try:
            opts, args = getopt.getopt(argv, "h", ["help"])
        except getopt.GetoptError, err:
            print str(err)
            self.usage()
            sys.exit(2)
        for o, a in opts:
            #print "o: ", o
            #print "a: ", a
            if o in ("-b", "--buzon"):
                self.opciones.print_buzon=True
            elif o in ("-r", "--rename"):
                self.opciones.rename = a
            elif o in ("-n","--nomina"):
                self.opciones.nomina = True
            elif o in ("-l","--longnames"):
                self.opciones.longnames = True
            elif o in ("-h","--help"):
                self.usage()
                sys.exit(0)

    def load_files(self, from_path):
        for dirname, subdirs, fnames in os.walk( os.path.abspath( from_path ) ) :
            if not self.recursive:  
                while len(subdirs) > 0:  
                    subdirs.pop()
            #print dirname, subdirs
            
            #dir_head="\n--- %s - %s ---"%(os.path.basename(os.path.abspath(os.path.join(dirname,os.path.pardir))), os.path.basename(dirname))
            for fnamex in sorted(fnames):
                if fnmatch.fnmatch( fnamex, '2015*.txt' ):
                    print os.path.join(dirname,fnamex)
                    edc = EstadoDeCuenta(os.path.join(dirname,fnamex))
                    edc.parse()
                    self.edcs.append(edc)
                    

if __name__ == "__main__":
    print os.getcwd()
    e = EstadosDeCuenta()
    e.parse_args(sys.argv[1:])
    e.load_files(os.getcwd())
   
    sys.exit(0)