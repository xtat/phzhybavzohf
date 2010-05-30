#!/usr/bin/env python
# 2010 Todd Troxell <ttroxell@debian.org>
#
# I am playing with fully automated substituion cypher solving...

import os
import sys
import csv
import re

class SubstitutionSolver(object):
    def __init__(self, cyphertxt, datadir="data/"):
        self.ewordfile = "/usr/share/dict/words"
        self.cyphertxt = open(cyphertxt, 'r')
        self.datadir = datadir
        self.__load_data()

    def __del__(self):
        self.cyphertxt.close()
        
    def __load_data(self):
        f = open(os.path.join(self.datadir, "letterfreq.csv"))
        dr = csv.reader(f)
        letterfreqs = {}
        for entry in dr:
            letterfreqs[entry[0]] = float(entry[1])
        f.close()
        sfreqs = sorted(letterfreqs.iteritems(), key=lambda (k,v): (v,k),
                     reverse=True)
        self.letterfreqs = sfreqs

        # load english words
        self.ewords = []
        f = open(self.ewordfile, 'r')
        for line in f:
            self.ewords.append(line.strip())
        f.close()

    def __munge(self, line):
        """remove things that would interfere with letter freq like newlines,
        lower() everything, remove numbers, etc"""
        outstr = re.sub('[^A-z]', '', line)
        outstr = outstr.lower()
        return outstr
                
    def letterfreq(self, input):
        counts = {}
        for line in input:
            line = self.__munge(line)
            if not line:
                continue
            for letter in line:
                try:
                    counts[letter] += 1
                except KeyError:
                    counts[letter] = 1
        counts = sorted(counts.iteritems(), key=lambda (k,v): (v,k),
                        reverse=True)
        return counts

    def __sanity(self):
        if not len(self.letterfreqs) == 26 or len(self.cypherfreqs) != 26:
            print "Number of letters != 26.  Exiting."
            sys.exit(-1)

    def __keygen(self):
        self.__sanity()
        key = {}
        for x in range(0,26):
            k = self.cypherfreqs[x][0]
            v = self.letterfreqs[x][0]
            key[k] = v

        if not self.check_key(key):
            print "failure!"
            sys.exit(0)
        return key

    def check_key(self, possible):
        out = self.__decrypt(possible)
        confidence = 0
        for token in out.split(' '):
            token = re.sub('[^A-z]', '', token)
            if token in self.ewords:
                confidence += 1
            else:
                confidence -= 1
        if confidence < 0:
            return False

    def __decrypt(self, key):
        self.cyphertxt.seek(0)
        output = ""
        for line in self.cyphertxt:
            new_line = ""
            for char in line:
                if re.match('[A-z]', char):
                    new_line += key[char.lower()]
                else:
                    new_line += char
            output += (new_line + '\n')
        return output
        
    def run(self):
        self.cypherfreqs = self.letterfreq(self.cyphertxt)
        self.key = self.__keygen()
        print self.key
        print self.__decrypt(self.key)
 
if __name__ == '__main__':
    app = SubstitutionSolver(sys.argv[1])
    app.run()

