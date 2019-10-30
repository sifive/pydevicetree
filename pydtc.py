#!/usr/bin/env python

import sys
from argparse import ArgumentParser

version = "0.0.1"

def main():
    argparser = ArgumentParser(description="Devicetree Compiler, but in Python")
    argparser.add_argument('inputfile', nargs=1, type=str, metavar="input file")
    argparser.add_argument('-q', '--quiet', action='count', help=" -q suppress warnings, -qq errors, -qqq all")
    argparser.add_argument('-I', '--in-format', type=str, help="Input formats are <dts | dtb>")
    argparser.add_argument('-o', '--out', type=str, help="Output file")
    argparser.add_argument('-O', '--out-format', type=str, help="Output formats are <dts | dtb>")
    argparser.add_argument('-v', '--version', action="version", version=version)

    argparser.parse_args()


#Usage: dtc [options] <input file>
#
#Options: -[qI:O:o:V:d:R:S:p:fb:i:H:sW:E:hv]
#  -q, --quiet                
#        Quiet: -q suppress warnings, -qq errors, -qqq all
#  -I, --in-format <arg>      
#        Input formats are:
#                dts - device tree source text
#                dtb - device tree blob
#                fs  - /proc/device-tree style directory
#  -o, --out <arg>            
#        Output file
#  -O, --out-format <arg>     
#        Output formats are:
#                dts - device tree source text
#                dtb - device tree blob
#                asm - assembler source
#  -V, --out-version <arg>    
#        Blob version to produce, defaults to %d (for dtb and asm output)
#  -d, --out-dependency <arg> 
#        Output dependency file
#  -R, --reserve <arg>        
#        tMake space for <number> reserve map entries (for dtb and asm output)
#  -S, --space <arg>          
#        Make the blob at least <bytes> long (extra space)
#  -p, --pad <arg>            
#        Add padding to the blob of <bytes> long (extra space)
#  -b, --boot-cpu <arg>       
#        Set the physical boot cpu
#  -f, --force                
#        Try to produce output even if the input tree has errors
#  -i, --include <arg>        
#        Add a path to search for include files
#  -s, --sort                 
#        Sort nodes and properties before outputting (useful for comparing trees)
#  -H, --phandle <arg>        
#        Valid phandle formats are:
#                legacy - "linux,phandle" properties only
#                epapr  - "phandle" properties only
#                both   - Both "linux,phandle" and "phandle" properties
#  -W, --warning <arg>        
#        Enable/disable warnings (prefix with "no-")
#  -E, --error <arg>          
#        Enable/disable errors (prefix with "no-")
#  -h, --help                 
#        Print this help and exit
#  -v, --version              
#        Print version and exit

if __name__ == "__main__":
    main()
