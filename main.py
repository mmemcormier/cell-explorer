#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 11:05:20 2021

@author: Marc M. E. Cormier
"""

from reader import ParseNeware
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.write("""
         # Let's plot some Neware data!
         """)

fdata = st.file_uploader("Load your Neware file here!")

@st.cache(persist=True)
def read_data(uploaded_bytes, cell_id):
    return ParseNeware(cell_id, all_lines=uploaded_bytes)

if fdata is not None:
    #nd = ParseNeware("Cell_ID", all_lines=fdata)
    nd = read_data(fdata, "Cell_ID")
    
    st.write("""
             ### Successfully loaded Neware file.
             """)
    
    plot_opts = st.sidebar.selectbox("What would you like to plot?",
                                     ('Discharge capacity', 'V-Q', 
                                      'dQ/dV'))
    

    
    rates = ['All'] + nd.get_rates()
    rate = st.sidebar.selectbox("Which C-rate would you like to see?",
                                tuple(rates))
    
    ncycs = nd.get_ncyc()
    if rate == 'All':
        cyc_nums = np.arange(1, ncycs+1)
    else:
        cyc_nums = np.array(nd.select_by_rate(rate))
        

    cyc_range = st.sidebar.slider("Cycle Numbers", 1, ncycs, (1, ncycs), 1)
    inds = np.where((cyc_nums <= cyc_range[1]) & (cyc_nums >= cyc_range[0]))[0]
    cycnums = cyc_nums[inds]
    num_cycs = len(cycnums)
    st.write("Plotting {0} cycles within range: ({1}, {2})".format(rate,
                                                               cyc_range[0],
                                                               cyc_range[1]))
    #cycnums = np.arange(cyc_range[0], cyc_range[1])
    #st.write("Cycle numbers", cycnums)
    cmap = st.sidebar.selectbox("Color pallette",
                                ('Default', 'viridis', 'rainbow'))
    if cmap == 'Default':
        avail_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = avail_colors*int(num_cycs/len(avail_colors) + 1)
    else:
        colors = plt.get_cmap(cmap)(np.linspace(0,1,num_cycs))
        
    smooth = st.sidebar.slider("dQ/dV moving average window width", 0, 10)
    if smooth == 0:
        smooth = None
                                 
    
    with plt.style.context('grapher'):
        fig, ax = plt.subplots(figsize=(5,4))
        
        if plot_opts == 'V-Q':
            for i in range(len(cycnums)):
                x, y = nd.get_vcurve(cycnum=cycnums[i])
                ax.plot(x, y, color=colors[i])
            ax.set_xlabel('Capacity (mAh)')
            ax.set_ylabel('Voltage (V)')
        elif plot_opts == 'dQ/dV':
            for i  in range(len(cycnums)):
                x, y = nd.get_dQdV(cycnum=cycnums[i], avgstride=smooth)
                ax.plot(x, y, color=colors[i])
            ax.set_xlabel('Voltage (V)')
            ax.set_ylabel('dQ/dV (mAh/V)')
        elif plot_opts == 'Discharge capacity':
            x, y = nd.get_discap()
            ax.plot(x, y, "o")
            ax.set_xlabel('Cycle Number')
            ax.set_ylabel('Specific Capacity (mAh/g)')

        #ax.plot(x, y)
        
    st.pyplot(fig)