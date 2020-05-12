#!/usr/bin/env python

import numpy as np
import pandas as pd
import re
from argparse import ArgumentParser


class ParseNeware():

    def __init__(self, newarefile):
        '''parse raw neware datafile into cycle, step, and record data\
           and put into pd df'''

        with open(newarefile, 'r', encoding='unicode_escape') as f:
            lines = f.readlines()
    
        # Replace single space between words with "_" to create column labels.
        cyclabels = re.sub(r'(\w+) (\w+)', r'\1_\2', lines[0])
        cyclabels = re.sub(r'(\w+) (\w+)', r'\1_\2', cyclabels)
        cyclabels = re.sub(r' ', r'', cyclabels)
        clabels = cyclabels.strip().split()

        steplabels = re.sub(r'(\w+) (\w+)', r'\1_\2', lines[1])
        steplabels = re.sub(r'(\w+) (\w+)', r'\1_\2', steplabels)
        steplabels = re.sub(r' ', r'', steplabels)
        slabels = steplabels.strip().split()

        reclabels = re.sub(r'(\w+) (\w+)', r'\1_\2', lines[2])
        reclabels = re.sub(r'(\w+) (\w+)', r'\1_\2', reclabels)
        reclabels = re.sub(r' ', r'', reclabels)
        rlabels = reclabels.strip().split()

        cyclnlen = len(clabels)
        print('Found {} cycle labels.'.format(cyclnlen))
        steplnlen = len(slabels)
        print('Found {} step labels.'.format(steplnlen))
        reclnlen = len(rlabels)
        print('Found record labels.'.format(reclnlen))

        # Parse out units from column labels and create dictionary of units
        # for cycle, step, and record data.

        self.cycunits = dict()
        newclabels = []
        cycheader = ''
        for l in clabels:
            try:
                m = re.search(r'\(.*\)', l)
                newlab = l[:m.start()]
                self.cycunits[newlab] = l[m.start()+1:m.end()-1]
                newclabels.append(newlab)
                cycheader = cycheader + '\t{}'.format(newlab)
            except:
                self.cycunits[l] = None
                newclabels.append(l)
                cycheader = cycheader + '\t{}'.format(l)

        self.stepunits = dict()
        stepheader = 'Cycle_ID'
        newslabels = ['Cycle_ID']
        for l in slabels:
            try:
                m = re.search(r'\(.*\)', l)
                newlab = l[:m.start()]
                self.stepunits[newlab] = l[m.start()+1:m.end()-1]
                newslabels.append(newlab)
                stepheader = stepheader + '\t{}'.format(newlab)
            except:
                self.stepunits[l] = None
                newslabels.append(l)
                stepheader = stepheader + '\t{}'.format(l)

        self.recunits = dict()
        recheader = 'Cycle_ID\tStep_ID'
        newrlabels = ['Cycle_ID', 'Step_ID']
        for l in rlabels:
            try:
                m = re.search(r'\(.*\)', l)
                newlab = l[:m.start()]
                if newlab == 'Vol':
                    newlab = 'Voltage'
                if newlab == 'Cap':
                    newlab = 'Capacity'
                self.recunits[newlab] = l[m.start()+1:m.end()-1]
                newrlabels.append(newlab)
                recheader = recheader + '\t{}'.format(newlab)
            except:
                self.recunits[l] = None
                newrlabels.append(l)
                recheader = recheader + '\t{}'.format(l)

        # Create header line for cycle, step, and record data
        cyc = ['{}\n'.format(cycheader)]
        step = ['{}\n'.format(stepheader)]
        rec = ['{}\n'.format(recheader)]

        # Separate cycle, step, and record data and write to 
        # file (needs to be changed to tmpfile) to be read 
        # in as DataFrame with inferred dtypes.
        for line in lines[3:]:
            l = line.strip().split()
            if len(l) >= cyclnlen:
                cycnum = l[0]
#                cyc.append(l)
                cyc.append(line)
            elif len(l) >= steplnlen:
                stepnum = l[0]
#                step.append([cycnum] + l)
                step.append('{0}{1}'.format(cycnum, line))
            else:
#                rec.append([cycnum, stepnum] + l)
                rec.append('{0}\t{1}{2}'.format(cycnum, stepnum, line))
        
        with open('cyc.dat', 'w') as f:
            for l in cyc:
                f.write(l)
        with open('step.dat', 'w') as f:
            for l in step:
                f.write(l)
        with open('rec.dat', 'w') as f:
            for l in rec:
                f.write(l)

        self.cyc = pd.read_csv('cyc.dat', sep='\t+', header=0, engine='python')
        self.step = pd.read_csv('step.dat', sep='\t+', header=0, engine='python')
        self.rec = pd.read_csv('rec.dat', sep='\t+', header=0, engine='python')
        '''
        # stuff for assinging directly to df instead of writing to file then 
        # using read_csv(). Issue is dtypes. Pandas infers when reading from file
        # but not if assigning df from lists. Once resovled, replace csv write/read.
        cyclnlen = len(cyc[0])
        if cyclnlen > len(newclabels):
            d = cyclnlen - len(newclabels)
            for i in range(d):
                newclabels.append('NA{}'.format(i+1))
        steplnlen = len(step[0])
        if steplnlen > len(newslabels):
            d = steplnlen - len(newslabels)
            for i in range(d):
                newslabels.append('NA{}'.format(i+1))
        reclnlen = len(rec[0])
        if reclnlen > len(newrlabels):
            d = reclnlen - len(newrlabels)
            for i in range(d):
                newrlabels.append('NA{}'.format(i+1))

        self.cyc = pd.DataFrame.from_records(cyc, columns=newclabels)
        self.step = pd.DataFrame.from_records(step, columns=newslabels)
        self.rec = pd.DataFrame.from_records(rec, columns=newrlabels)
        '''
        if self.recunits['Voltage'] == 'mV':
            self.rec['Voltage'] = self.rec['Voltage'] / 1000
            self.recunits['Voltage'] = 'V'


    # The following set of functions are designed to be intuitive 
    # for people in the lab that want to get particular information
    # from cycling data.

    def get_charge(self, cycnum=1):
        '''
        Get charge data for a particular cycle.
        '''
        try:
            cycle = self.rec.loc[self.rec['Cycle_ID'] == cycnum]
        except:
            raise Exception('Cycle {} does not exist. Input a different cycle number.'.format(cycnum))

        stepnums = cycle['Step_ID'].unique()
        chg = cycle.loc[cycle['Step_ID'] == stepnums[0]]
        voltage = chg['Voltage'].values
        capacity = chg['Capacity'].values

        return voltage, capacity

    def get_discharge(self, cycnum=1):
        '''
        Get discharge data for a particular cycle.
        '''
        try:
            cycle = self.rec.loc[self.rec['Cycle_ID'] == cycnum]
        except:
            raise Exception('Cycle {} does not exist. Input a different cycle number.'.format(cycnum))

        stepnums = cycle['Step_ID'].unique()
        chg = cycle.loc[cycle['Step_ID'] == stepnums[-1]]
        voltage = dchg['Voltage'].values
        capacity = dchg['Capacity'].values

        return voltage, capacity

    def get_cycle(self, cycnum=1):
        '''
        Get cycle data for a particular cycle.
        TODO: Need to deal with error handling properly.
        '''
#        try:
        cycle = self.rec.loc[self.rec['Cycle_ID'] == cycnum]
#        except:
#            raise RuntimeError('Cycle {} does not exist. Input a different cycle number.'.format(cycnum))

        stepnums = cycle['Step_ID'].unique()
#        if len(stepnums) == 0:
#            print('Cycle {} does not exist. Input a different cycle number.'.format(cycnum))
#            return

        chg = cycle.loc[cycle['Step_ID'] == stepnums[0]]
        Vchg = chg['Voltage'].values
        Cchg = chg['Capacity'].values

        dchg = cycle.loc[cycle['Step_ID'] == stepnums[-1]]
        Vdchg = dchg['Voltage'].values
        Cdchg = dchg['Capacity'].values

        voltage = np.concatenate((Vchg, Vdchg))
        capacity = np.concatenate((Cchg, -Cdchg+Cchg[-1]))

        return voltage, capacity

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('newarefile')
    args = parser.parse_args()

    # this does nothing currently. Need to think about 
    # what command line utils to include.
    nd = ParseNeware(args.newarefile)


