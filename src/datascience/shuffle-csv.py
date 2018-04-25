#!/usr/local/bin/python2.7
# encoding: utf-8
'''
-- shortdesc

shuffle and take a sample from csv, or shuffle and split into train and set

@author:     Maksim Mikhalkou

@contact:    maksim_mikhalkou@epam.com
@deffield    updated: Updated
'''

import sys
import os
import pandas as pd

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.31
__date__ = '2018-04-14'
__updated__ = '2018-04-25'

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

  Created by Maksim Mikhalkou on %s.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, 
                            help='set verbosity level [default: %(default)s]')
        parser.add_argument("--take", dest="records_to_take", type=int, default=0,
                            help="records to take from input file (0 for all) [default: %(default)s]", 
                            metavar="NUMBER")
        parser.add_argument('-d', '--destination', dest='result_destination', default='{}-shuffled-{}.csv', 
                            help='result destination and name', metavar='PATH' )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="path", help="paths to the source CSV file [default: %(default)s]", 
                            metavar="PATH")
        parser.add_argument('--split', dest='split',  action='count', default=0,
                            help='split files into 2 (like test and train)')

        # Process arguments
        args = parser.parse_args()

        path = args.path
        verbose = args.verbose
        result_destination = args.result_destination
        records_to_take = args.records_to_take
        split = args.split

        if verbose > 0:
            print("Verbose mode on")
            
        if verbose > 0:
            print('Loading input data from {}'.format(path))
        input_file = pd.read_csv(path)
        docs_count = input_file.shape[0]
        
        if verbose > 0:
            print('Input data contains {} records'.format(docs_count))
        if records_to_take > 0:
            if records_to_take > docs_count:
                print('Warning: unable take {} records as file contains only {} records'
                      .format(records_to_take, docs_count))
                records_to_take = docs_count
        else:
            #if records_to_take <= 0 - take all records
            records_to_take = docs_count
        
        if result_destination == '{}-shuffled-{}.csv':
            result_destination = '{}-shuffled-{}.csv'.format(
                os.path.splitext(os.path.basename(path))[0], records_to_take)
            result_destination_test = '{}-shuffled-{}_test.csv'.format(
                os.path.splitext(os.path.basename(path))[0], docs_count - records_to_take)
        elif split>0:
            result_destination_test = result_destination + '_{}'.format(docs_count 
                                                                        - records_to_take)
        
        train = input_file.sample(n=records_to_take)
        train.to_csv(result_destination, index=False)

        if verbose>0:
            print('Shuffled file with {} records has been saved to {}'
                  .format(records_to_take ,os.path.abspath(result_destination)))
            
        if split>0:
            test=input_file.drop(train.index)
            test.to_csv(result_destination_test, index=False)
            
            if verbose>0:
                print('Split is enabled. Shuffled file with {} records has been saved to {}'
                      .format(docs_count - records_to_take ,os.path.abspath(result_destination_test)))
        
        
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