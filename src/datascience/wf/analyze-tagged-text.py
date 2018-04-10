#!/usr/local/bin/python2.7
# encoding: utf-8
'''
-- shortdesc

is a description

It defines classes_and_methods

@author:     Maksim Mikahlkou

@contact:    maksim_mikhalkou@epam.com
@deffield    updated: Updated
'''

import sys
import os
import statistics as stat
import pandas as pd
import lxml.etree as ET

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from unittest.mock import inplace

__all__ = []
__version__ = 0.2
__date__ = '2018-04-05'
__updated__ = '2018-04-05'

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

def tag_dict():
		tdict = dict()
		tdict['occurrences'] = []
		tdict['errors'] = []
		tdict['word_counts'] = []
		return tdict

def tag_dict_doc():
		tdict = dict()
		tdict['occurrences'] = 0
		tdict['errors'] = 0
		tdict['word_counts'] = []
		return tdict


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
''' % (program_shortdesc, str(__date__))

		try:
				# Setup argument parser
				parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
				parser.add_argument('-v', '--verbose', dest='verbose', action='count', default=0, help='set verbosity level [default: %(default)s]')
				parser.add_argument('-d', '--destination', dest='report_destination', default='_report.csv', help='report file destination and name', metavar='PATH' )
				parser.add_argument('-t', '--taggedtext', dest='tagged_text_column',  default='tagged_text', help='text column name [default: %(default)s]', metavar='COLUMN_NAME' )
				parser.add_argument('-V', '--version', action='version', version=program_version_message)
				parser.add_argument(dest='path', help='paths to csv to analyze [default: %(default)s]', metavar='path')

				# Process arguments
				args = parser.parse_args()

				path = args.path
				verbose = args.verbose
				report_destination = args.report_destination
				tagged_text_column = args.tagged_text_column

				if verbose > 0:
						print("Verbose mode on")

				if verbose > 0:
						print('Loading input data from {}'.format(path))
				input_file = pd.read_csv(path)
				docs_count = input_file.shape[0]
				if verbose > 0:
						print('Input data contains {} records'.format(docs_count))

				if tagged_text_column not in input_file.columns:
						print('Error: {} column does not exist'.format(tagged_text_column))
						return 4
				elif verbose>0:
						print('Checked: columns exist.')

				data = dict()

				for index, row in input_file.iterrows():
						text = row[tagged_text_column]
						text= text.replace('<br>', '<br />')
						if '<document>' not in text:
							text = '<document>' + text + '</document>'
						parser = ET.XMLParser(recover=True)
						document = ET.fromstring(text, parser=parser)
						extraction_tags = document.findall('.//*[@class="extraction-tag"]')
						document_data = dict()
						if verbose > 0:
								print('row {}: found {} extraction tags'.format(index, len(extraction_tags)))

						for etag in extraction_tags:
								if etag.tag not in document_data:
										document_data[etag.tag] = tag_dict_doc()
								document_data[etag.tag]['occurrences'] += 1
								if etag.text != etag.get('data-value'):
										document_data[etag.tag]['errors'] += 1
								ttext = etag.text if etag.text is not None else ''
								document_data[etag.tag]['word_counts'].append(len(ttext.split()))

						for k,v in document_data.items():
								if k not in data:
										data[k] = tag_dict()
								data[k]['occurrences'].append(v['occurrences'])
								data[k]['errors'].append(v['errors'])
								data[k]['word_counts'].append(v['word_counts'])

				columns = ['col_name', 'occurs', 'occurs avg. per doc', 'occurs median', 'occurs max ', 'documents count',
										'documents where occurs', 'OCR error rate', 'words avg.',
										'words median', 'words min', 'words max' ]
				stats = pd.DataFrame(columns=columns)

				for k,v in data.items():
						occurs = v['occurrences']

						ocount = sum(occurs)
						omax = max(occurs)
						omean = stat.mean(occurs)
						omed = stat.median(occurs)
						oindocs = sum(x>0 for x in occurs)
						docs = docs_count

						errors = v['errors']
						errrate = sum(errors) / ocount

						words = v['word_counts']
						words_flat = [observation for document in words for observation in document]
						wmean = stat.mean(words_flat)
						wmed = stat.median(words_flat)
						wmin = min(words_flat)
						wmax = max(words_flat)

						field_stats = pd.DataFrame([[k, ocount, omean, omed, omax, docs, oindocs,
																				errrate, wmean, wmed, wmin, wmax]],
																				columns=columns)
						stats = pd.concat([stats, field_stats])


				stats.to_csv(report_destination)

				if verbose>0:
						print('Report saved: {}'.format(os.path.abspath(report_destination)))

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
