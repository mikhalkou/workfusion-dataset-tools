#!/usr/local/bin/python2.7
# encoding: utf-8
'''
 -- shortdesc

 is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2018 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import re
import pandas as pd

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2018-04-09'
__updated__ = '2018-04-09'

DEBUG = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg
    
class Filter():
    def __init__(self, filter_str):
        self.filter_src = 'self.exec_result =' + re.sub(r'{(\S+?)}', r'x["\1"]', filter_str)
    
    def filter(self, x):
        exec(self.filter_src)
        return self.exec_result

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2018 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='set verbosity level [default: %(default)s]')
        parser.add_argument('-d', '--destination', dest='result_destination', default='filtered.csv', help='report file destination and name', metavar='PATH' )
        parser.add_argument('-f', '--filter', dest='filter', default='filtered.csv', help='pandas like syntax logic expression: "({COLUMN_NAME}==value) & ({COLUMN_NAME}!=value) ..."', metavar='filter' )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="path", help="path to a source csv file [default: %(default)s]", metavar="path")

        # Process arguments
        args = parser.parse_args()

        path = args.path
        verbose = args.verbose
        filter = Filter(args.filter)
        destination = args.result_destination

        if verbose > 0:
            print("Verbose mode on")

        if verbose > 0:
            print('Loading input data from {}'.format(path))
        input_file = pd.read_csv(path)
        if verbose > 0:
            docs_count = input_file.shape[0]
            print('Input data contains {} records'.format(docs_count))
                        
        filtered = input_file[filter.filter(input_file)]
        if verbose > 0:
            docs_count = filtered.shape[0]
            print('Filtered data contains {} records'.format(docs_count))
            
        filtered.to_csv(destination, index=False)
        if verbose > 0:
             print('Filtered data saved to {}'.format(os.path.abspath(destination)))
                        
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = '_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())