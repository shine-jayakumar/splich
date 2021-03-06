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
from configparser import ConfigParser
import sys

VERSION = 'v.1.4'

VERBOSE = False


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

    vvprint(f'Source file: {file}')
    vvprint(f'Size: {fsize}')

    segment_size = 0

    if parts:
        segment_size = fsize // parts
    else:
        segment_size = chunk_size
    
    if segment_size < 1:
        raise ValueError('At least 1 byte required per part')

    vvprint(f'Segment Size: {segment_size}')

    fdir, fname = os.path.split(file)
    # fname = fname.split('.')[0]
    fname = os.path.splitext(fname)[0]
    
    vvprint('Generating hash')
    hash = gethash(file)
    start_time = datetime.today().strftime("%m%d%Y_%H%M")

    vvprint(f'Hash: {hash}\n\n')
    vvprint(f'Reading file: {file}')

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
            vvprint(f'{part_filename} Segment size: {segment_size} bytes')
            with open(part_filename, 'wb') as chunk_fh:
                chunk_fh.write(chunk)
            fpart += 1

        # hashfile generation
        hashfilename = f'{fname}_hash_{start_time}'
        hashfile_path = os.path.join(fdir, hashfilename)
        vvprint(f'Hashfile: {hashfile_path}')
        with open(hashfile_path, 'w') as hashfile:
            hashfile.write(hash)
        
        # auto-stitch config file generation
        vvprint('Generating auto-stitch config file')
        if generate_stitch_config(filename=file, hashfile=hashfilename):
            vvprint('Saved stitch.ini')
        else:
            vvprint('Could not create auto-stitch config. Stitch files manually.')

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
    # fname = fname.split('.')[0]
    fname = os.path.splitext(fname)[0]
    
    file_parts = glob.glob(os.path.join(fdir,  f'{fname}_*.prt'))
    file_parts = sort_file_parts(file_parts)
    
    if not file_parts:
        raise FileNotFoundError('Split files not found')

    if outfile:
        # if just the filename
        if os.path.split(outfile)[0] == '':
            # create the file in input dir (fdir)
            outfile = os.path.join(fdir, outfile)
    
    vvprint(f'Output: {outfile or file}')

    with open(outfile or file, 'wb') as fh:
        for filename in file_parts:
            buffer = b''
            vvprint(f'Reading {filename}')
            with open(filename, 'rb') as prt_fh:
                buffer = prt_fh.read()
                fh.write(buffer)

    vvprint(f'Written {os.path.getsize(outfile or file)} bytes')
    
    if hashfile:
        print('Verifying hash')
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
    

def vvprint(text):
    '''
    print function to function only when verbose mode is on
    '''
    global VERBOSE
    if VERBOSE:
        print(text)


def getpartno(filepart):
    '''
    Returns the part number from a part filename
    Ex: flask_05112022_1048_3.prt -> 3
    '''
    return int(filepart.split('_')[-1].split('.')[0])


def sort_file_parts(file_part_list):
    '''
    Returns a sorted list of part filenames based on the part number
    Ex: ['flask_05112022_1048_3.prt', 'flask_05112022_1048_1.prt', 'flask_05112022_1048_2.prt'] ->
        ['flask_05112022_1048_1.prt', 'flask_05112022_1048_2.prt', 'flask_05112022_1048_3.prt']
    '''
    # creates list of (prt_no, part)
    fparts = [(getpartno(prt), prt) for prt in file_part_list]
    fparts.sort(key=lambda x: x[0])
    fparts = [prt[1] for prt in fparts]
    return fparts
        

def generate_stitch_config(filename, hashfile):
    '''
    Generates auto-stitch config file
    '''
    try:
        with open('stitch.ini', 'w') as configfile:
            config = ConfigParser()
            config.add_section('stitch')
            config.set('stitch', 'filename', filename)
            config.set('stitch', 'hashfile', hashfile)

            config.add_section('settings')
            config.set('settings', 'verbose', 'True')
            config.write(configfile)
    except Exception as ex:
        print(f'Error while creating auto-stitch config file: {str(ex)}')
        stitch_config_path = os.path.join(os.getcwd(), 'stitch.ini')
        if os.path.exists(stitch_config_path):
            os.remove(stitch_config_path)
        return False
    return True


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
parser.add_argument('-vv', '--verbose',  action='store_true', help='verbose mode')
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {VERSION}')

# If config file exists - auto stitch
if os.path.exists(os.path.join(os.getcwd(), 'stitch.ini')):
    print('Found config file - stitch.ini')
    config = ConfigParser()
    config.read('stitch.ini')
    fname = config.get('stitch', 'filename')
    hashfile = config.get('stitch', 'hashfile')
    verbose = config.getboolean('settings', 'verbose')

    if verbose == True:
        VERBOSE = True
    try:
        file_stitch(fname, outfile=None, hashfile=hashfile)
    except FileNotFoundError as ex:
        print(f'Error: {str(ex)}')
    
    sys.exit()


args = parser.parse_args()

if args.split and (not args.parts and not args.size):
    parser.error('--split requires --parts or --size to be specified')

if args.verbose:
    VERBOSE = True

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
