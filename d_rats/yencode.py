#!/usr/bin/python
#
# Copyright 2008 Dan Smith <dsmith@danplanet.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
import sys

DEFAULT_BANNED = b"\x11\x13\x1A\00\xFD\xFE\xFF"
OFFSET = 64

def yencode_buffer(buf, banned=None):
    if not banned:
        banned = DEFAULT_BANNED

    # python2 compatibility hack
    if isinstance(banned, str):
        banned = bytearray(banned)

    banned += b"="
    out = b""
    yesc = b"="

    if isinstance(out, str):
        out = bytearray(out)
    if isinstance(yesc, str):
        yesc = bytearray(yesc)

    for char in buf:
        if char in banned:
            if isinstance(char, str):
                char = ord(char)
            out += yesc + int_to_byte((char + OFFSET) % 256)
        else:
            out += int_to_byte(char)

    return out

def ydecode_buffer(buf):
    out = b""
    
    # Needed for python2 compatibility
    if isinstance(out, str):
        out = bytearray(out)
    if isinstance(buf, str):
        buf = bytearray(buf)

    i = 0
    yesc = ord("=")
    while i < len(buf):
        char = buf[i]
        if char == yesc:
            i += 1
            v = buf[i] - OFFSET
            if v < 0:
                v += 256
            out += int_to_byte(v)
        else:
            out += int_to_byte(char)

        i += 1

    return out

def int_to_byte(data):
    # python2 compatibility hack
    if isinstance(data, str):
        data = ord(data)
    if sys.version_info[0] > 2:
        result = chr(data).encode('ISO-8859-1')
    else:
        result = chr(data)
    return result

if __name__=="__main__":
    import sys

    action = '-t'
    argc = len(sys.argv) - 1
    if argc > 0:
        action = sys.argv[1]

    infile = None
    outfile = None
    if argc > 1:
        infile = sys.argv[2]
    elif action != '-t':
        print('No input file specified.')
        print('python(2|3) -m d_rats.yencode [-t] [encoded_file]')
        print('python(2|3) -m d_rats.yencode [-d encoded_file [decoded_file]')
        print('python(2|3) -m d_rats.yencode [-e infile encoded_file ]')
        sys.exit(1)

    if action == '-t':
        inbuf = DEFAULT_BANNED + b'foobar'
        for i in range(0, 255):
            inbuf += int_to_byte(i)
        if argc > 2:
            outfile = sys.argv[2]
    else:
        f = open(sys.argv[2], mode='rb')
        inbuf = f.read()
        f.close()
        if argc > 3:
            outfile = sys.argv[3]

    if isinstance(inbuf, str):
        inbuf = bytearray(inbuf)

    if action == "-e":
        outbuf = yencode_buffer(inbuf)
    elif action == '-d':
        outbuf = ydecode_buffer(inbuf)
    else:
        fail = 0
        outbuf = yencode_buffer(inbuf)
        buffer = ydecode_buffer(outbuf)
        for i in range(0, len(buffer)):
            if buffer[i] != inbuf[i]:
                fail += 1
        if fail > 0:
            print('[FAILED] %s bytes different' % fail)
        else:
            print('[PASSED]')

    if outfile:
        f = open(outfile, 'wb')
        f.write(outbuf)
        f.close

