# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@qmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

assert str is not bytes

DEFAULT_OUT='out.xml'
DEFAULT_EXTENSION='xml'

class FilezillaCollectorValueError(ValueError):
    pass

def none_log(*args, **kwargs):
    pass

def filezilla_collector(
        path_list,
        out=None,
        log=None,
        followlinks=None,
        extension=None):
    from os import walk
    from os.path import isfile, isdir, join, samefile
    
    if out is None:
        out = DEFAULT_OUT
    if log is None:
        log = none_log
    if followlinks is None:
        followlinks = False
    if extension is None:
        extension = DEFAULT_EXTENSION
    
    xml_list = []
    
    for path in path_list:
        if isfile(path):
            if path.endswith('.{}'.format(extension)):
                xml_list.append(path)
                log('scheduled file {path!r}'.format(path=path))
                
                continue
        elif isdir(path):
            log('scanning directory {path!r} for scheduling...'.
                    format(path=path))
            for dirpath, dirnames, filenames in walk(
                    path, followlinks=followlinks):
                for filename in filenames:
                    subpath = join(dirpath, filename)
                    
                    if isfile(subpath) and isfile(out) and \
                            samefile(subpath, out):
                        continue
                    elif not subpath.endswith('.{}'.format(extension)):
                        continue
                    
                    xml_list.append(subpath)
                    log('  scheduled file {path!r}'.format(path=subpath))
            
            continue
        
        log('skipped path {path!r}'.format(path=path))
    
    out_lines = []
    for path in xml_list:
        log('processing file {path!r}...'.format(path=path), end=' ')
        try:
            xml_lines = []
            with open(path, 'r') as fd:
                for line in fd:
                    xml_lines.append(line)
            
            if not xml_lines:
                raise FilezillaCollectorValueError()
            if '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' not in xml_lines[0]:
                raise FilezillaCollectorValueError()
            if '<FileZilla3>' not in xml_lines[1]:
                raise FilezillaCollectorValueError()
            if '<Queue>' not in xml_lines[2]:
                raise FilezillaCollectorValueError()
            if '</FileZilla3>' not in xml_lines[-1]:
                raise FilezillaCollectorValueError()
            if '</Queue>' not in xml_lines[-2]:
                raise FilezillaCollectorValueError()
            
            out_lines += xml_lines[3:-2]
        except (FilezillaCollectorValueError, EnvironmentError):
            log('ERROR')
            from traceback import print_exc
            print_exc()
        else:
            log('PASS')
    
    log('writing out {path!r}...'.format(path=out), end=' ')
    with open(out, 'w') as fd:
        fd.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
        fd.write('<FileZilla3>\n')
        fd.write('    <Queue>\n')
        for line in out_lines:
            fd.write('{}'.format(line))
        fd.write('    </Queue>\n')
        fd.write('</FileZilla3>\n')
    log('PASS')
