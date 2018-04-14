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
from bokeh.themes import default

__all__ = []
__version__ = 0.1
__date__ = '2018-04-05'
__updated__ = '2018-04-05'

DEBUG = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = 'E: %s' % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def escape_file_name(string):
    return re.sub(r'[\W]', '_', str(string))

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = 'v%s' % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split('\n')[1]
    program_examples = '''
Examples: 
    python split-csv.py ../folder/file.csv -d ../html -t image_link_tagged
     python split-csv.py  ../folder/file.csv -v -d ../xmk -o xml -t image_link_tagged -i submissionUUID
'''
    program_license = '''%s %s
  Created by Maksim Mikhalkou on %s.
''' % (program_shortdesc, program_examples, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-o', '--format', dest='output_format', default='html', 
                            help='recurse into subfolders [default: %(default)s]')
        parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, 
                            help='set verbosity level [default: %(default)s]')
        parser.add_argument('-d', '--destination', dest='destination_folder', default='splitted_data', 
                            help='output folder destinaton', metavar='PATH' )
        parser.add_argument('-i', '--id', dest='id_column', 
                            help='id column name (is used to generate file name) [default: %(default)s]', 
                            metavar='COLUMN_NAME' )
        parser.add_argument('-t', '--text', dest='text_column',  default='tagged_text', 
                            help='text column name (not applicable for json output format) [default: %(default)s]', 
                            metavar='COLUMN_NAME' )
        parser.add_argument('-c', '--columns', dest='column_list', nargs='*', 
                            help='column list to export (only applicable for json output format) [default: %(default)s]', 
                            metavar='COLUMN_NAME' )
        parser.add_argument('-r', '--regex', dest='column_regex', 
                            help='column regex to export (only applicable for json output format) [default: %(default)s]', 
                            metavar='RE' )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest='path', help='paths to csv file to split [default: %(default)s]', metavar='path')

        # Process arguments
        args = parser.parse_args()

        path = args.path
        verbose = args.verbose
        output_format = args.output_format
        destination_folder = args.destination_folder
        id_column = args.id_column
        text_column = args.text_column
        column_list = args.column_list
        column_regex = args.column_regex

        if verbose > 0:
            print('Verbose mode on')
            print('Output format is {}'.format(output_format))
        
        if verbose > 0:
            print('Loading input data from {}'.format(path))
        input_file = pd.read_csv(path)
        if verbose > 0:
            print('Input data contains {} records'.format(input_file.shape[0]))
            
        if output_format in ['html', 'xml', 'txt']:
            is_columns_exists = True
            if id_column is not None:
                if id_column not in input_file.columns:
                    is_columns_exists = False
                    print('Error: {} column does not exist'.format(id_column))
                    
            if text_column not in input_file.columns:
                is_columns_exists = False
                print('Error: {} column does not exist'.format(text_column))
                
            if not is_columns_exists:
                return 4
            
            if is_columns_exists and verbose>0:
                print('Checked: columns exist.')
                
        elif output_forat in []: #['csv', 'json']:
            pass
        else:
            print('Error:{} is unsupported'.format(output_format))
            return 3
            
        if not os.path.exists(destination_folder):
            if verbose > 0:
                print('Creating directory {}'.format(os.path.abspath(destination_folder)))
            os.makedirs(destination_folder)
        else:
            print('Warning: directory {} is already exists!'.format(os.path.abspath(destination_folder)))
            
        if output_format in ['html', 'xml', 'txt']:
            for index, row in input_file.iterrows():
                file_name = '{}.{}'.format(str(index), output_format)
                if id_column is not None:
                    file_name = '{}.{}'.format(escape_file_name(row[id_column]), output_format)
                text = row[text_column]
                file_name = os.path.abspath(destination_folder) + '/' + file_name
                f = open(file_name, 'w', encoding='utf-8')
                f.write(text)
                f.close()
                if verbose>0:
                    print("{} has been written".format(file_name))
        elif output_forat in []: #['csv', 'json']:
            pass

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG:
            raise(e)
        indent = len(program_name) * ' '
        sys.stderr.write(program_name + ': ' + repr(e) + '\n')
        sys.stderr.write(indent + '  for help use --help')
        return 2

if __name__ == '__main__':
    if DEBUG:
        sys.argv.append('-h')
        sys.argv.append('-v')
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = '_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open('profile_stats.txt', 'wb')
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())