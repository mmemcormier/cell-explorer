#!/usr/bin/env python

import pandas as pd
import numpy as np
from argparse import ArgumentParser

def rate_map(record_df, curr_thresh=2.0):
    
# see df.query
    cyc_nums = pd.unique(record_df['Cycle_ID'])
    current = np.zeros(len(cyc_num))
    for i in range(len(cyc_nums)):
        tmp = record_df[record_df['Cycle_ID'] == cyc_num[i]]
        tmp = tmp[tmp['Current(mA)'] > 0.0]
        current[i] = tmp['Current(mA)'].mean()

# now need to parse different rates ...


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument()
    args = parser.parse_args()
