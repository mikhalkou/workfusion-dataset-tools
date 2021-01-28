#!/usr/local/bin/python3.9
# encoding: utf-8
'''
 -- shortdesc

Joins files from a folder to a csv file

@author:     Maksim Mikhalkou

@contact:    maksim@mikhalkou.com
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
__date__ = '2021-01-27'
__updated__ = '2021-01-27'

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


def main(argv=None):  # IGNORE:C0111
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
    python join-files-to-csv.py ../folder/ -d /home/user/output.csv
    python join-files-to-csv.py  ../folder/ -v -d output.csv
'''
    program_license = '''%s %s
  Created by Maksim Mikhalkou on %s.
''' % (program_shortdesc, program_examples, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                            help='set verbosity level [default: %(default)s]')
        parser.add_argument('-d', '--destination', dest='destination_file', default='output.csv',
                            help='output CSV file destinaton', metavar='PATH')
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest='path', help='paths to folder with html or xml files to join [default: %(default)s]',
                            metavar='path')

        # Process arguments
        args = parser.parse_args()

        path = args.path
        verbose = args.verbose
        destination_file = args.destination_file

        if os.path.exists(destination_file):
            print("Error. Destination file already exists.")
            return 9

        if verbose > 0:
            print('Loading input data from folder {}'.format(path))

        output_df = pd.DataFrame(columns=['tagged_text', 'filename'])

        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith(".html") or filename.endswith(".htm") or filename.endswith(".xml"):
                    if verbose > 0:
                        print('Reading file: {}'.format(filename))
                    file = open(os.path.join(root, filename), 'r')
                    output_df = output_df.append({'tagged_text': file.read(), 'filename': filename}, ignore_index=True)
                    # print(os.path.join(root, file))

        destination_folder = os.path.dirname(destination_file)
        if not os.path.exists(destination_folder):
            if verbose > 0:
                print('Creating directory {}'.format(os.path.abspath(destination_folder)))
            os.makedirs(destination_folder)

        output_df.to_csv(destination_file, sep=',', encoding='utf-8', index=False)
        if verbose > 0:
            print('{} files were joined.'.format(output_df.shape[0]))

        return 0
    except KeyboardInterrupt:
        # handle keyboard interrupt ###
        return 0
    except Exception as e:
        if DEBUG:
            raise (e)
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
