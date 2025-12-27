#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2025 ZeeTwii.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy # needed for numpy.float32
from gnuradio import gr # needed for gnuradio
import socket # needed for udp socket 

class adsbGen(gr.sync_block):
    """
    docstring for block adsbGen
    """
    def __init__(self, ipAddress='0.0.0.0', portNum='7331', sampleRate=2000000):
        
        # Our minimum sample rate is 2MHz, twice that of the Mode S signal rate of 1MHz due to how we do Manchester encoding
        if sampleRate < 2000000:
            print("Sample rate too low, setting multipler to 1")
            self.multiplier = 1
        else:
            self.multiplier = int(sampleRate / 2000000)
            print("Setting multiplier to: " + str(self.multiplier))

        # create UDP socket
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # bind socket
        self.recSocket.bind((str(ipAddress), int(portNum)))

        print(f"Binding Socket to: {str(ipAddress)} , {str(portNum)}")

        # set socket to nonblocking
        self.recSocket.setblocking(False)
        self.recSocket.settimeout(0)

        # set mode S preamble
        self.preamble = "1010000101000000"

        # remaining message buffer
        self.messageRemaining = ''
        
        gr.sync_block.__init__(self,
            name="adsbGen",
            in_sig=None,
            out_sig=[numpy.float32, ])


    def work(self, input_items, output_items):
        out = output_items[0]
        # <+signal processing here+>
        out[:] = numpy.float32(0)

        # try to receive data from socket
        try:
            # this should be a binary string
            socketMessage = self.recSocket.recv(4096).decode('utf-8')

            message = ""

            # add preamble with multiplier
            for bit in self.preamble:
                if bit == '1':
                    message += '1' * self.multiplier
                elif bit == '0':
                    message += '0' * self.multiplier
                else:
                    print("Received invalid bit in preamble: " + str(bit))

            # do manchester encoding with multiplier
            for bit in socketMessage:
                if bit == '1':
                    message += '1' * self.multiplier
                    message += '0' * self.multiplier
                elif bit == '0':
                    message += '0' * self.multiplier
                    message += '1' * self.multiplier
                else:
                    print("Received invalid bit: " + str(bit))
            
            print("Generated message: " + str(message))
            self.messageRemaining += message
        except socket.error:
            pass # no data received

        # check if there is remaining message to send
        if len(self.messageRemaining) > 0:

            if len(self.messageRemaining) >= len(out):
                # fill the output buffer
                for i in range(len(out)):
                    if self.messageRemaining[i] == '1':
                        out[i] = numpy.float32(1)
                    else:
                        out[i] = numpy.float32(0)
                
                # update remaining message
                self.messageRemaining = self.messageRemaining[len(out):]

            else:
                # fill what we can
                for i in range(len(self.messageRemaining)):
                    if self.messageRemaining[i] == '1':
                        out[i] = numpy.float32(1)
                    else:
                        out[i] = numpy.float32(0)
                
                # clear remaining message
                self.messageRemaining = ''


        


        return len(output_items[0])
