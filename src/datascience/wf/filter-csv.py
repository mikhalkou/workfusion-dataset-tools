#!/usr/local/bin/python2.7
# encoding: utf-8
'''
 -- shortdesc

 is a description

It defines classes_and_methods

@author:     Maksim Mikhalkou

@contact:    maksim_mikhalkou@epam.com
@deffield    updated: Updated
'''

import sys
import os
import re
import pandas as pd

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.3
__date__ = '2018-04-09'
__updated__ = '2018-04-11'

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
        parser.add_argument('-f', '--filter', dest='filter', help='pandas query syntax logic expression: "COLUMN_NAME==value and COLUMN_NAME>value & ..."', metavar='filter' )
        parser.add_argument('-c', '--columns', dest='columns', help='list of columns to keep', metavar='COLUMNS LIST', nargs="*" )
        parser.add_argument('-t', '--taggedtext', dest='tagged_text_column',  default='tagged_text', help='text column name [default: %(default)s]', metavar='COLUMN_NAME' )
        parser.add_argument('--restore_tagged_text', dest='restore_tagged_text', action='count', default=0, help='restore tagged text column [default: %(default)s]' )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="path", help="path to a source csv file [default: %(default)s]", metavar="path")

        # Process arguments
        args = parser.parse_args()

        path = args.path
        verbose = args.verbose
        filter_query = args.filter
        columns = args.columns
        destination = args.result_destination
        tagged_text_column = args.tagged_text_column
        restore_tagged_text = args.restore_tagged_text

        if verbose > 0:
            print("Verbose mode on")

        if verbose > 0:
            print('Loading input data from {}'.format(path))
        input_file = pd.read_csv(path)
        if verbose > 0:
            docs_count = input_file.shape[0]
            print('Input data contains {} records'.format(docs_count))
            
        if restore_tagged_text > 0 and tagged_text_column not in input_file.columns:
            print('Error: {} column does not exist'.format(tagged_text_column))
            return 4
        
        if filter_query is not None:               
            filtered = input_file.query(filter_query)#[filter.filter(input_file)]
            if verbose > 0:
                docs_count = filtered.shape[0]
                print('Filtered data contains {} records'.format(docs_count))
        else:
            filtered = input_file
            
        if restore_tagged_text > 0:
            filtered[tagged_text_column] = filtered[tagged_text_column].apply(
                lambda x: x if '<document>' in x else '<document>' + x + '</document>')
            if verbose > 0:
                print('Restoring data set is finished.')

        if columns is not None and len(columns)>0:
            filtered = filtered.filter(items=columns)
            if verbose > 0:
                print('Removed all columns except: {}'.format(columns))
                for col in columns:
                    if col not in input_file.columns:
                        print('Warning {} does not exist.'.format(col))
            
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