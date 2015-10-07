import os
import re
import sys
from datetime import datetime



BANAMEX_HEADER='FECHA,DESCRIPCION,DEPOSITOS,RETIROS,SALDO'
date_rx   = '(?P<date>\d\d-\d\d-\d\d\d\d)'
desc_rx   = '(?P<desc>[^"]*)'
debit_rx  = '(?P<debit>\d+(,\d{3})*(\.\d*)?)?'
credit_rx = '(?P<credit>\d+(,\d{3})*(\.\d*)?)?'
saldo_rx  = '(?P<saldo>\d+(,\d{3})*(\.\d*)?)?'
state_rx  = '(?P<state>[^"]*)'
curr_rx   = '(?P<currency>[^"]*)'
BANAMEX_TRANSACTION = re.compile('"' + date_rx + '","' + desc_rx + '","' + debit_rx + '","' + credit_rx + '","' + saldo_rx + '","' + state_rx + '","' + curr_rx + '"')

class BanamexTransaction:
    def __init__ (self, date, description, ammount, balance):
        self.date = date
        self.description = description
        self.ammount = ammount
        self.balance = balance

    def __str__(self, *args, **kwargs):
        res_str = self.date.strftime('%m/%d/%Y') + '  ' + self.description + '  ' + str(self.ammount) + '  ' + str(self.balance)
        return res_str

class BanamexParser:
    def __init__(self, argv):
        self.argv = argv
        self.file = ''
        self.out = ''
        self.transactions = []
        self.account = ''

    def usage(self):
        print "\nUSAGE: %.65s [options]" % sys.argv[0]
        print "OPTIONS:"
        print "-f, --file              specify file to parse"
        print "-o, --out               specify the output file"
        print "-a, --account           specify the account to use"
        
    def parse_args(self):
        import getopt
        try:
            opts, args = getopt.getopt(self.argv, "f:ho:a:",
            ["--file=","--help","--out=","--account="])
        except getopt.GetoptError, err:
            print str(err)
            self.usage()
            return -1

        for o, a in opts:
            if o in ("-f", "--file"):
                self.file = a
            elif o in ("-h", "--help"):
                self.usage()
                sys.exit(0)
                return -1
            elif o in ("-o", "--out"):
                self.out = a
            elif o in ("-a", "--account"):
                self.account = a
            else:
                assert False, "unknown option"
        return 0;
    
    def parse_line(self, line):
        if BANAMEX_TRANSACTION.match(line):
            m = BANAMEX_TRANSACTION.search(line)
            credit = m.group('credit') 
            date   = m.group('date')
            desc   = m.group('desc')
            debit  = m.group('debit')
            credit = m.group('credit')
            saldo  = m.group('saldo')
            state  = m.group('state')
            curr   = m.group('currency')
            date_object = datetime.strptime(date, '%d-%m-%Y')
            ammount = 0
            if credit and len(credit) > 0:
                ammount = float(credit.replace(',', ''))
            elif debit and len(debit) > 0:
                ammount = - float(debit.replace(',', ''))
            
            if saldo and len(saldo) > 0:
                balance = float(saldo.replace(',',''))
            trans = BanamexTransaction(date_object,desc, ammount, balance)
            return trans
        


    def main ( self ):
        if self.parse_args() != 0:
            sys.exit(0)
        if self.file == '' or self.out == '':
            self.usage()
            sys.exit(0)
        for line in open(self.file):
            transaction = self.parse_line(line)
            if transaction != None:
             self.transactions.append(transaction)
        
        print 'Date,Account Name,Category,Description,Amount,Check,Payee,Note'
        for tr in self.transactions:
            tr_str =                tr.date.strftime('%d/%m/%Y') 
            tr_str = tr_str + ',' + self.account
            tr_str = tr_str + ',' # empty category 
            tr_str = tr_str + ',' + tr.description.replace(',', ' ')
            tr_str = tr_str + ',' + str(tr.ammount)
            tr_str = tr_str + ',' #+ '#empty check'
            tr_str = tr_str + ',' #+ '#empty payee'
            tr_str = tr_str + ',' #+ '#empty note'
            print tr_str



if __name__ == "__main__":
    bp = BanamexParser(sys.argv[1:])
    ec = bp.main()
    sys.exit(ec)

