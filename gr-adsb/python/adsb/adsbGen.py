#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 ZeeTwii.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np # needed for gnuradio
from gnuradio import gr # needed for gnuradio
import socket # needed for UDP socket

class adsbGen(gr.sync_block):
    """
    docstring for block adsbGen
    """
    def __init__(self, portNum):
        
        # create UDP socket
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # bind socket
        self.recSocket.bind((str('0.0.0.0'), int(portNum)))

        print(f"Binding Socket to: {str('0.0.0.0')} , {str(portNum)}")

        # set socket to nonblocking
        self.recSocket.setblocking(False)
        self.recSocket.settimeout(0)

        gr.sync_block.__init__(self,
            name="adsbGen",
            in_sig=None,
            out_sig=[np.float32])


    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        
        msg = ''
        
        try:
            msg =  self.recSocket.recv(4096).decode()
            #print(f"Got: {str(msg)}")
        except socket.error:
            msg = '00000000000000000000'
        
        
        # test if out or msg is shorter: only needed for startup
        if len(msg) > len(out):
            size = len(out)
        else:
            size = len(msg)
        
        for i in range(size):
            if msg[i] == '1':
                out[i] = float(1)
            else:
                out[i] = float(0)
        
        out[:] = float(0)
        return len(output_items[0])
