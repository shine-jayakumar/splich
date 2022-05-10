# Splich.py
# Splits files into parts, or in chunk_size
# Splich is a file splitting tool that allows you to split a file into parts, and reassembles them

# https://github.com/shine-jayakumar/splich

# Author: Shine Jayakumar
# https://github.com/shine-jayakumar
#
# MIT License

# Copyright (c) 2022 Shine Jayakumar

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import argparse
import hashlib
from datetime import datetime

VERSION = 'v.1.0'


def file_split(file, parts=None, chunk_size=None):
    '''
    Splits files into parts, or in chunk_size
    '''
    if not file:
        return False
    if not parts and not chunk_size:
        return False
        
    fsize = os.path.getsize(file)

    if chunk_size and chunk_size > fsize:
        raise ValueError('Chunk size cannot be greater than file size')

    segment_size = 0

    if parts:
        segment_size = fsize // parts
    else:
        segment_size = chunk_size
    
    if segment_size < 1:
        raise ValueError('At least 1 byte required per part')

    fdir, fname = os.path.split(file)
    fname = fname.split('.')[0]
    
    hash = gethash(file)
    start_time = datetime.today().strftime("%m%d%Y_%H%M")

    with open(file,'rb') as fh:
        fpart = 1
        while fh.tell() != fsize:
            if parts:
                # check if this is the last part
                if fpart == parts:
                    # size of the file - wherever the file pointer is
                    # the last part would contain segment_size + whatever is left of the file
                    segment_size = fsize - fh.tell()

            chunk = fh.read(segment_size)
            part_filename = os.path.join(fdir, f'{fname}_{start_time}_{fpart}.prt')
            with open(part_filename, 'wb') as chunk_fh:
                chunk_fh.write(chunk)
            fpart += 1
        
        with open(f'{fname}_hash_{start_time}', 'w') as hashfile:
            hashfile.write(hash)

        return True   


def file_stitch(file, outfile=None, hashfile=None):
    '''
    Stitches the parts together
    '''
    # d:\\somedir\\somefile.txt to 
    # d:\\somedir and somefile.txt

    if not file:
        return False

    fdir, fname = os.path.split(file)
    fname = fname.split('.')[0]
    
    file_parts = glob.glob(os.path.join(fdir,  f'{fname}_*.prt'))
    
    buffer = b''
    for filename in file_parts:
        with open(filename, 'rb') as fh:
            buffer += fh.read()

    if outfile:
        # if just the filename
        if os.path.split(outfile)[0] == '':
            # create the file in input dir (fdir)
            outfile = os.path.join(fdir, outfile)

    with open(outfile or file, 'wb') as fh:
        fh.write(buffer)
    
    if hashfile:
        if checkhash(outfile or file, hashfile):
            print('Hash verified')
        else:
            print('Hash verification failed')


def gethash(file):
    '''
    Returns the hash of file
    '''
    hash = None
    with open(file, 'rb') as fh:
        hash = hashlib.sha256(fh.read()).hexdigest()
    return hash


def checkhash(file, hashfile):
    '''
    Compares hash of a file with original hash read from a file
    '''
    curhash = None
    orghash = None
    curhash = gethash(file)
    with open(hashfile, 'r') as fh:
        orghash = fh.read()

    return curhash == orghash
    
        
# ====================================================
# Argument parsing
# ====================================================
description = "Splits a file into parts/Stitches split files"
usage = "splich.py filename [--split (--parts no_of_parts|--size chunk_size)|--stitch]"
examples="""
Examples:
splich.py ebook.pdf --split --size 100000
splich.py ebook.pdf --split --parts 10
splich.py ebook.pdf --stitch
splich.py ebook.pdf --stitch -o ebook_stitched.pdf
"""
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=description,
    usage=usage,
    epilog=examples,
    prog='splich')

# required arguments
parser.add_argument('filename', type=str, help='File to split or stitch')

# optional arguments
parts_or_size = parser.add_mutually_exclusive_group()
parts_or_size.add_argument('-p', '--parts', type=int, metavar='', help='number of parts to split in')
parts_or_size.add_argument('-s', '--size', type=int, metavar='', help='size of each chunk')

split_or_stich = parser.add_mutually_exclusive_group()
split_or_stich.add_argument('-sp', '--split', action='store_true', help='split the file')
split_or_stich.add_argument('-st', '--stitch', action='store_true', help='stitch the file')

parser.add_argument('-hf', '--hashfile',  type=str, metavar='', help='file containing hash of the original file')
parser.add_argument('-o', '--outfile',  type=str, metavar='', help='write stitched file to (default - same as the input file)')
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}')

# if args.prox and (args.lport is None or args.rport is None):
#     parser.error("--prox requires --lport and --rport.")

args = parser.parse_args()

if args.split and (not args.parts and not args.size):
    parser.error('--split requires --parts or --size to be specified')


file = args.filename

if args.split:
    try:
        if args.parts:
            file_split(file, parts=args.parts)
        else:
            file_split(file, chunk_size=args.size)
    except ValueError as ex:
        print(f'Error : {str(ex)}')
    except FileNotFoundError as ex:
        print(f'Error: {str(ex)}')

if args.stitch:
    outfile = args.outfile
    hashfile = args.hashfile
    try:
        file_stitch(file, outfile, hashfile)
    except FileNotFoundError as ex:
        print(f'Error: {str(ex)}')
