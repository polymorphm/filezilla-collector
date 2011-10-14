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

def safe_print(*args, sep=None, end=None, file=None):
    if sep is None:
        sep = ' '
    if end is None:
        end = '\n'
    if file is None:
        from sys import stdout as sys_stdout
        file = sys_stdout
    
    def safe_conv(value):
        encoding = getattr(file, 'encoding', None) or 'utf-8'
        
        if isinstance(value, bytes):
            safe_value = value
        elif isinstance(value, str):
            safe_value = value.encode(encoding, 'replace')
        else:
            safe_value = str(value).encode(encoding, 'replace')
        
        return safe_value
    
    print_str = safe_conv(sep).join(safe_conv(v) for v in args) + safe_conv(end)
    
    file.buffer.write(print_str)
    file.buffer.flush()
