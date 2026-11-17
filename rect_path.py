#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:55:36 2026

@author: fedora
"""


import numpy as np
import streamlit as st

from funcs import plot_rec, get_g, plot_Smit, calc_L, plot_Smit2


st.sidebar.header("Катушка")
st.header("Катушка")
st.sidebar.header("Геометрические параметры")
r = st.sidebar.slider(
    "Радиус катушки r, мм",
    min_value=0,
    max_value=100,
    value=50,
    step=1
)
dr = st.sidebar.slider(
    "Зазор dr, мм",
    min_value=1.0,
    max_value=50.0,
    value=5.0,
    step=0.5
)
w = st.sidebar.slider(
    "Ширина w, мм",
    min_value=1.0,
    max_value=50.0,
    value=5.0,
    step=0.5
)
n = st.sidebar.slider(
    "Количество витков",
    min_value=1,
    max_value=int(r / (dr + w)) + 1,
    value=int(r / (dr + w)) + 1,
    step=1
)


st.sidebar.header("Электрические параметры")
R = st.sidebar.slider(
    "Сопротивление R, Ом",
    min_value=1.0,
    max_value=100.0,
    value=10.0,
    step=0.5
)


Z0 = st.sidebar.selectbox(
    "Опорное сопротивление Z₀, Ом",
    [25, 50, 75, 100],
    index=1
)

f_min = st.sidebar.number_input(
    "Начальная частота, Гц",
    min_value=1.0,
    max_value=1e9,
    value=1e3,
    format="%.0f"
)

f_max = st.sidebar.number_input(
    "Конечная частота, Гц",
    min_value=1.0,
    max_value=1e9,
    value=1e6,
    format="%.0f"
)
if f_max <= f_min:
    st.error("Конечная частота должна быть больше начальной.")
    st.stop()


f = np.logspace(
    np.log10(f_min),
    np.log10(f_max),
    1000
)

st.set_page_config(layout="wide")
col1, col2 = st.columns([1, 1], vertical_alignment='center')

###############################################################################
fig1, d_in, d_out = plot_rec(r, dr, w, n)

L = calc_L(d_in, d_out, n)
gamma, Z = get_g(R, f, L, Z0)

fig2 = plot_Smit(gamma, Z0)

###############################################################################
st.write(f'Индуктивность L = {L:.2e} Гн')
with col1:
    st.pyplot(fig1)
with col2:
    st.pyplot(fig2)



st.sidebar.header("Антенна")
f_ant_min = 300e6
f_ant_max = 500e6
f_ant = np.linspace(f_ant_min, f_ant_max, 1001)

f0 = st.sidebar.slider(
    "Опорная частота f0, МГц",
    min_value=f_ant_min/1e6,
    max_value=f_ant_max/1e6,
    value=433.0,
    step=1.0,
) * 1e6


k = st.sidebar.slider(
    "Коэффициент магнитной связи k",
    min_value=0.01,
    max_value=1.0,
    value=0.01,
    step=0.01
)

R_ant = st.sidebar.slider(
    "Сопротивление R, Ом",
    min_value=1.0,
    max_value=100.0,
    value=10.0,
    step=0.5,
    key='antenna',
)


L_ant = st.sidebar.slider(
    "Индуктивность L, нГн",
    min_value=1.0,
    max_value=200.0,
    value=100.0,
    step=0.5
) * 1e-9

C_ant = st.sidebar.slider(
    "Емкость C, пФ",
    min_value=1.0,
    max_value=10.0,
    value= 1.35, #1 / ((2 * np.pi * f0)**2 * L_ant) / 1e-12,
    step=0.1
) * 1e-12


w = 2 * np.pi * f_ant

# Параметры антенны
Z0 = 50

gamma, Z = get_g(R, f_ant, L, Z0)

# 1. Импеданс антенны (последовательный RLC)
Z_ant = (R_ant + 1j * w * L_ant + 1 / (1j * w * C_ant))
# 3. Взаимная индуктивность
M = k * np.sqrt(L_ant * L)

# 4. Внесённый импеданс от катушки
Z_reflected = (w * M)**2 / Z

# 5. Новый импеданс антенны
Z_ant_coupled = Z_ant + Z_reflected

# 6. Коэффициенты отражения
gamma_0 = (Z_ant - Z0) / (Z_ant + Z0)
gamma_coupled = (
    (Z_ant_coupled - Z0) /
    (Z_ant_coupled + Z0)
)


st.header("Антенна")
_, col3, _ = st.columns([1, 2, 1], vertical_alignment='center')
fig3 = plot_Smit2(Z0, gamma_0, gamma_coupled, f_ant, f0)
with col3:
    st.pyplot(fig3)