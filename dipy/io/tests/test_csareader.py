""" Testing Siemens CSA header reader
"""
import os
from os.path import join as pjoin
import sys
import struct

import numpy as np

import dipy.io.csareader as csa
import dipy.io.dwiparams as dwp

from nose.tools import assert_true, assert_false, \
     assert_equal, assert_raises

from numpy.testing import assert_array_equal, assert_array_almost_equal

from dipy.testing import parametric


data_path = pjoin(os.path.dirname(__file__), 'data')

CSA2_B0 = open(pjoin(data_path, 'csa2_b0.bin')).read()
CSA2_B1000 = open(pjoin(data_path, 'csa2_b1000.bin')).read()


@parametric
def test_csas0():
    for csa_str in (CSA2_B0, CSA2_B1000):
        csa_info = csa.read(csa_str)
        yield assert_equal(csa_info['type'], 2)
        yield assert_equal(csa_info['n_tags'], 83)
        tags = csa_info['tags']
        yield assert_equal(len(tags), 83)
        n_o_m = tags['NumberOfImagesInMosaic']
        yield assert_equal(n_o_m['items'], [48])
    csa_info = csa.read(CSA2_B1000)
    b_matrix = csa_info['tags']['B_matrix']
    yield assert_equal(len(b_matrix['items']), 6)
    b_value = csa_info['tags']['B_value']
    yield assert_equal(b_value['items'], [1000])


@parametric
def test_csa_params():
    for csa_str in (CSA2_B0, CSA2_B1000):
        csa_info = csa.read(csa_str)
        n_o_m = csa.get_n_mosaic(csa_info)
        yield assert_equal(n_o_m, 48)
        snv = csa.get_slice_normal(csa_info)
        yield assert_equal(snv.shape, (3,))
        yield assert_true(np.allclose(1, 
                np.sqrt((snv * snv).sum())))
        amt = csa.get_acq_mat_txt(csa_info)
        yield assert_equal(amt, '128p*128')
    csa_info = csa.read(CSA2_B0)
    b_matrix = csa.get_b_matrix(csa_info)
    yield assert_equal(b_matrix, None)
    b_value = csa.get_b_value(csa_info)
    yield assert_equal(b_value, 0)
    g_vector = csa.get_g_vector(csa_info)
    yield assert_equal(g_vector, None)
    csa_info = csa.read(CSA2_B1000)
    b_matrix = csa.get_b_matrix(csa_info)
    yield assert_equal(b_matrix.shape, (3,3))
    # check (by absence of error) that the B matrix is positive
    # semi-definite. 
    q = dwp.B2q(b_matrix)
    b_value = csa.get_b_value(csa_info)
    yield assert_equal(b_value, 1000)
    g_vector = csa.get_g_vector(csa_info)
    yield assert_equal(g_vector.shape, (3,))
    yield assert_true(
        np.allclose(1, np.sqrt((g_vector * g_vector).sum())))