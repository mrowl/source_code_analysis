'''
'''
import logging
import optparse
import os
import subprocess

from foursquare.source_code_analysis.scala.scala_import_sorter import ScalaImportSorter
from foursquare.source_code_analysis.scala.scala_unused_import_remover import ScalaUnusedImportRemover

VERSION = '0.1'

log = logging.getLogger()

def get_command_line_args():
    opt_parser = optparse.OptionParser(usage='%prog [options] scala_source_file_or_dir(s)', version='%prog ' + VERSION)
    opt_parser.add_option('--log_level', type='choice', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO', help='Log level to display on the console.')
    opt_parser.add_option('--backup', action='store_true', dest='backup', default=False,
        help='If specified, we back up modified files with a .bak suffix before rewriting them.')
    opt_parser.add_option('--fancy', action='store_true', dest='fancy', default=False,
        help='Whether to separate java, javax, scala and scalax imports and put them first.')

    (options, args) = opt_parser.parse_args()
    return options, args

if __name__ == "__main__":
    (options, scala_source_files) = get_command_line_args()
    numeric_log_level = getattr(logging, options.log_level, None)
    if not isinstance(numeric_log_level, int):
      raise Exception('Invalid log level: %s' % options.log_level)
    logging.basicConfig(level=numeric_log_level)
    if not scala_source_files:
        origin_sha = 'origin/master'
        ps_git = subprocess.Popen(('git', 'diff', '--name-only', origin_sha), stdout=subprocess.PIPE)
        ps_sort = subprocess.Popen(('sort'), stdin=ps_git.stdout, stdout=subprocess.PIPE)
        ps_uniq = subprocess.Popen(('uniq'), stdin=ps_sort.stdout, stdout=subprocess.PIPE)
        ps_grep = subprocess.Popen(('grep', 'scala$'), stdin=ps_uniq.stdout, stdout=subprocess.PIPE)
        ps_git.stdout.close()
        output = ps_grep.communicate()[0]
        scala_source_files = [ str(f) for f in output.decode('ascii').splitlines() ]
    [ log.info('Operating on: %s', f) for f in scala_source_files ]
    import_sorter = ScalaImportSorter(options.backup, options.fancy)
    import_sorter.apply_to_source_files(scala_source_files)
    import_rewriter = ScalaUnusedImportRemover(options.backup)
    import_rewriter.apply_to_source_files(scala_source_files)
    log.info('Done!')
