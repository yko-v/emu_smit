#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 18:39:49 2026

@author: fedora
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import skrf as rf

def plot_rec(R, dr, w, N):
    dn = dr + w
    x0 = 0
    y0 = 0
    
    bord_x = np.array([0, 0, 2*R, 2*R] * N)
    bord_x = bord_x.reshape(N, 4)
    
    bord_y = np.array([0, 2*R, 2*R, dn] * N)
    bord_y = bord_y.reshape(N, 4)
    
    for i in range(1, N):
        bord_x[i] = bord_x[i-1] + np.array([dn, dn, -dn, -dn])
        bord_y[i] = bord_y[i-1] + np.array([dn, -dn, -dn, dn])
        
    bord_y[0][0] = dn 
    dx = np.diff(bord_x)
    DX = np.append(dx.T, -dx.T[1]).reshape(4, N).T
    DX[:,1] = DX[:,1] + w
    DX[:,3] = DX[:,3] + w + dr
    dy = np.diff(bord_y)
    DY = np.append(dy.T, dy.T[1]).reshape(4, N).T
    
    dx2 = dx[:, 1]
    dx2 = dx2[dx2!=0].flatten()
    d_out = dx2[0]
    d_in = dx2[-1]    
    
    DX[DX==0] = w
    DY[DY==0] = w
    
    fig, ax = plt.subplots(figsize=(8, 8))
    for i in range(len(bord_x) - 1):
        for j in range(4):
            x0, y0 = bord_x[i][j], bord_y[i][j]
            dx, dy = DX[i][j], DY[i][j]      
            #print(x0, y0, dx, dy)
            rect = Rectangle([x0, y0], dx, dy) 
            ax.add_patch(rect)
        
    plt.xlim(-dn + w/2, 2*R + dn)
    plt.ylim(w, 2*R + dn)
    return fig, d_in, d_out


def get_g(R, f, L, Z0):
    # Комплексный импеданс последовательной RL-модели
    Z = R + 1j * 2 * np.pi * f * L
    # Коэффициент отражения
    gamma = (Z - Z0) / (Z + Z0)
    return gamma, Z

def calc_L(d_in, d_out, n):
    #L1 = K1 * mu0 * n**2 * d_avg / (1 + K2 * ro)
    mu0 = 4 * np.pi * 1e-7
    ro = (d_out - d_in) / (d_out + d_in)
    d_avg = 0.5 * (d_out + d_in)
    L = 1.27 * mu0 * n**2 * d_avg / 2 * (np.log10(2.07/ro) + 0.18*ro + 0.13*ro**2)
    return L

def plot_Smit(gamma, Z0):
    fig, ax = plt.subplots(figsize=(5, 5))
    rf.plotting.smith(ax=ax, chart_type="z", ref_imm=Z0, draw_labels=True)

    ax.plot(gamma.real, gamma.imag, label="Катушка RL")

    ax.plot(gamma.real[0], gamma.imag[0], "o") 
    ax.plot(gamma.real[-1], gamma.imag[-1], "s")
    return fig

def plot_Smit2(Z0, gamma_0, gamma_coupled, f, f0):
    fig, ax = plt.subplots()

    rf.plotting.smith(
        ax=ax,
        chart_type="z",
        ref_imm=Z0,
        draw_labels=True
    )

    '''
    ax.plot(    
        gamma_0.real,
        gamma_0.imag,
        label="Антенна без катушки"
    )
    '''

    # Центральная частота
    idx = np.argmin(np.abs(f - f0))

    ax.plot(
        gamma_0.real[idx],
        gamma_0.imag[idx],
        "o",
        label="433 МГц без катушки"
    )

    ax.plot(
        gamma_coupled.real[idx],
        gamma_coupled.imag[idx],
        "s",
        label="433 МГц с катушкой"
    )
    '''
    ax.plot(
        gamma_coupled.real,
        gamma_coupled.imag,
        label="Антенна с катушкой"
    )
    '''
   # ax.legend()
   # ax.set_title("Влияние катушки на согласование UHF-антенны")
    return fig
