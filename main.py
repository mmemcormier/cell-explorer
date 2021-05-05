#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  5 11:05:20 2021

@author: Marc M. E. Cormier
"""

from reader import ParseNeware
import streamlit as st
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
             ## Successfully loaded Neware file.
             """)
    cap, volt = nd.get_vcurve()
    with plt.style.context('grapher'):
        fig, ax = plt.subplots(figsize=(4,4))
        ax.plot(cap, volt)
        ax.set_xlabel('Capacity (mAh)')
        ax.set_ylabel('Voltage (V)')
        
    st.pyplot(fig)