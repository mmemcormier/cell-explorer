#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 11:05:20 2021

@author: Marc M. E. Cormier
"""

from reader import ParseNeware
import streamlit as st
from bokeh.plotting import figure, save
import bokeh.palettes as bp
from bokeh.io import curdoc, export_png
import numpy as np
from pathlib import Path
#import shutil as sh
#import os
import matplotlib.pyplot as plt
#os.environ['MPLCONFIGDIR'] = "./.matplotlib"
import matplotlib

#cfgdir = matplotlib.get_configdir()
#st.write(cfgdir)
#cwd = os.getcwd()
#sh.copy("{}/mpl_styles/grapher.mplstyle".format(cwd),
#        "{}/stylelib/grapher.mplstyle".format(cfgdir))

# The below HACK still does not solve the failure of Streamlit when 
# running on Streamlit share. Large files crash! 
# HACK This only works when we've installed streamlit with pipenv, so the
# permissions during install are the same as the running process
STREAMLIT_STATIC_PATH = Path(st.__path__[0]) / 'static'
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = (STREAMLIT_STATIC_PATH / "downloads")
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

st.write("""
         # Let's plot some Neware data!
         """)

fdata = st.file_uploader("Load your Neware file here!")

@st.cache(persist=True)
def read_data(uploaded_bytes, cell_id):
    return ParseNeware(cell_id, all_lines=uploaded_bytes,
                       tmppath=DOWNLOADS_PATH)

@st.cache(persist=True)
def voltage_curves(cycnums, active_mass=None):
    cap_list = []
    volt_list = []
    for i in range(len(cycnums)):
        cap, volt = nd.get_vcurve(cycnum=cycnums[i], active_mass=active_mass)
        cap_list.append(cap)
        volt_list.append(volt)
    
    return cap_list, volt_list

        
@st.cache(persist=True)
def dQdV(cycnums, avgstride=None, active_mass=None):
    volt_list = []
    dqdv_list = []
    for i  in range(len(cycnums)):
        volt, dqdv = nd.get_dQdV(cycnum=cycnums[i], active_mass=active_mass,
                                 avgstride=smooth)
        volt_list.append(volt)
        dqdv_list.append(dqdv)

    return volt_list, dqdv_list


if fdata is not None:
    #nd = ParseNeware("Cell_ID", all_lines=fdata)
    nd = read_data(fdata, "Cell_ID")
    
    st.write("""
             ### Successfully loaded Neware file.
             """)
    
    plot_opts = st.sidebar.selectbox("What would you like to plot?",
                                     ('Discharge capacity', 
                                      #'Specific discharge capacity',
                                      'V-Q', 
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
    
    active_mass = st.sidebar.number_input("Active material mass (in grams):")
    if active_mass == 0.0:
        active_mass = None
    else:
        st.write("Calculating specific capacity using {} g active material".format(active_mass))
    #cycnums = np.arange(cyc_range[0], cyc_range[1])
    #st.write("Cycle numbers", cycnums)
    cmap = st.sidebar.selectbox("Color pallette",
                                ('Default', 'viridis', 'cividis'))
    if cmap == 'Default':
        avail_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = avail_colors*int(num_cycs/len(avail_colors) + 1)
    elif cmap == 'viridis':
        colors = bp.viridis(num_cycs)
    elif cmap == 'cividis':
        colors = bp.cividis(num_cycs)
        
    #else:
    #    colors = plt.get_cmap(cmap)(np.linspace(0,1,num_cycs))
        
    smooth = st.sidebar.slider("dQ/dV moving average window width", 0, 10)
    if smooth == 0:
        smooth = None
                                 
#    with plt.style.context('grapher'):
#        fig, ax = plt.subplots(figsize=(5,4))
    #curdoc().theme = 'dark_minimal' # not working
    p = figure(plot_width=800, plot_height=400)
    
    if plot_opts == 'V-Q':
        caps, volts = voltage_curves(cycnums, active_mass=active_mass)
        
        if active_mass is not None:
            p.xaxis.axis_label = 'Specific Capacity (mAh/g)'
        else:
            p.xaxis.axis_label = 'Capacity (mAh)'
        p.yaxis.axis_label = 'Voltage (V)'
        for cap, volt, color in zip(caps, volts, colors):
            p.line(cap, volt, color=color, line_width=2.0)


    elif plot_opts == 'dQ/dV':
        volts, dqdvs = dQdV(cycnums, active_mass=active_mass,
                            avgstride=smooth)
        
        p.xaxis.axis_label = 'Voltage (V)'
        if active_mass is not None:
            p.yaxis.axis_label = 'dQ/dV (mAh/V/g)'
        else:
            p.yaxis.axis_label = 'dQ/dV (mAh/V)'
        for volt, dqdv, color in zip(volts, dqdvs, colors):
            p.line(volt, dqdv, color=color, line_width=2.0)

    elif plot_opts == 'Discharge capacity':
        cycs, dcap = nd.get_discap(active_mass=active_mass)
        if active_mass is not None:
            p.yaxis.axis_label = 'Specific Capacity (mAh/g)'
        else:
            p.yaxis.axis_label = 'Capacity (mAh)'
        p.xaxis.axis_label = 'Cycle Number'
        p.circle(cycs, dcap, size=4, color="black", alpha=0.75)
        
    #elif plot_opts == 'Discharge capacity':
        #x, y = nd.get_discap(specific=True)
        #p.circle(x, y, size=4, color="black", alpha=0.75)
        #ax.plot(x, y, "o")
        #ax.set_xlabel('Cycle Number')
        #ax.set_ylabel('Specific Capacity (mAh/g)')

        #ax.plot(x, y)
        
    #st.pyplot(fig)
    st.bokeh_chart(p, use_container_width=True)
    rel_path = st.text_input("Save figure to: C://")
    savepng_button = st.button("Save figure to png!")
    savehtml_button = st.button("Save figure to html! (interactive plot)")

    home_path = Path("/home/mmemc")
    fig_path = home_path / rel_path
    if savehtml_button is True:
        save(p, filename="{}.html".format(fig_path))
    if savepng_button is True:
        export_png(p, filename="{}.png".format(fig_path))