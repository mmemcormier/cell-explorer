#!/usr/bin/env python

import pandas as pd
from argparse import ArgumentParser


def read_raw(newarefile):
    '''parse raw neware datafile into cycle, step, and record data\
       and put into pd df'''
    with open(newarefile, 'r') as f:
        lines = f.readlines()
    
    cyclabels = lines[0].replace(' ', '_')
    steplabels = lines[1].replace(' ', '_')
    reclabels = lines[2].replace(' ', '_')
    cyclnlen = len(cyclabels.strip().split())
    steplnlen = len(steplabels.strip().split())
    reclnlen = len(reclabels.strip().split())

# Need to make new dataframes with same labels containing units for all quantities.
    cyc = [cyclabels]
    step = ['{0}{1}'.format(cyclabels.strip().split()[0],
                            steplabels)]
    rec = ['{0}\t\t{1}{2}'.format(cyclabels.strip().split()[0],
                                  steplabels.strip().split()[0],
                                  reclabels)]
    for line in lines[3:]:
        l = line.strip().split()
        if len(l) > steplnlen:
            cycnum = l[0]
            cyc.append(line)
        elif len(l) > reclnlen:
            stepnum = l[0]
            step.append('{0}{1}'.format(cycnum, line))
        else:
            rec.append('{0}\t\t{1}{2}'.format(cycnum, stepnum, line))

# temporarily write parsed data to file. To be removed for production
# should think about writing to tmp files, reading into df, and returning df
    with open('cyc.dat', 'w') as f:
        for l in cyc:
            f.write(l)
    with open('step.dat', 'w') as f:
        for l in step:
            f.write(l)
    with open('rec.dat', 'w') as f:
        for l in rec:
            f.write(l)

    cyc = pd.read_csv('cyc.dat', sep='\t+', header=0)
    step = pd.read_csv('step.dat', sep='\t+', header=0)
    rec = pd.read_csv('rec.dat', sep='\t+', header=0)

    return cyc, step, rec

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--newarefile')
    args = parser.parse_args()

    read_raw(args.newarefile)
