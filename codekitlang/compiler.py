# -*- coding: utf-8 -*-

import logging
import os
import re


logger = logging.getLogger(__name__)
special_comment_re = re.compile(
    r'(?P<wrapper><!--\s*(?:'
    r'@(?:import|include)\s+(?P<filenames>.*?)'
    r'|'
    r'[@$](?P<variable>[a-zA-Z][^\s:=]*)\s*(?:[\s:=]\s*(?P<value>.*?))?'
    r')-->)',
    re.DOTALL | re.IGNORECASE | re.LOCALE | re.MULTILINE | re.UNICODE
)


class CompileError(Exception):
    pass


class FileNotFoundError(CompileError):
    pass


class UnknownEncodingError(CompileError):
    pass


class VariableNotFoundError(CompileError):
    pass


def parse_string(s):
    """
    @type s: str (Python2.X unicode)
    @rtype: [(str, str), ...]
    """
    parsed = []
    pos = 0
    for m in special_comment_re.finditer(s):
        if m.start('wrapper') > pos:
            parsed.append(('NOOP', s[pos:m.start('wrapper')]))
        if m.group('filenames'):
            for filename in m.group('filenames').split(','):
                filename = filename.strip().strip('\'"')
                parsed.append(('JUMP', filename))
        elif m.group('value'):
            value = m.group('value').strip()
            parsed.append(('STOR', (m.group('variable'), value)))
        else:  # m.group('variable')
            parsed.append(('LOAD', m.group('variable')))
        pos = m.end('wrapper')
    parsed.append(('NOOP', s[pos:]))
    return parsed


def get_filepath(filename, base_path, framework_paths):
    """
    @type filename: str
    @type base_path: str
    @type framework_paths: [str, ...]
    @rtype: str
    """
    _, ext = os.path.splitext(filename)
    if not ext:
        filename += '.kit'
        ext = '.kit'
    if ext == '.kit':
        prefixes = ('', '_')
        paths = (base_path,) + tuple(framework_paths)
    else:
        prefixes = ('',)
        paths = (base_path,)
    for prefix in prefixes:
        for path in paths:
            filepath = os.path.abspath(os.path.join(path, filename))
            basename = os.path.basename(filename)
            if prefix and not basename.startswith(prefix):
                filepath = os.path.join(
                    os.path.dirname(filepath),
                    prefix + os.path.basename(filename)
                )
            if os.path.exists(filepath):
                logger.debug('Using %s for %s', filepath, filename)
                return filepath
    return None


def bytes_to_str(b, encoding_hints=None):
    """
    @type b: bytes (Python2.X str)
    @type encoding_hints: [str, ...]
    @rtype: (str, [(str, str), ...])
    """
    # TODO: not implemented now
    return 'utf-8', unicode(b, encoding='utf-8', errors='strict')


def get_file_content(filepath, encoding_hints=None):
    """
    @type filepath: str
    @type encoding_hints: [str, ...]
    @rtype: str
    """
    with open(filepath, 'rb') as fp:
        b = fp.readall()
    return bytes_to_str(b, encoding_hints)


def parse_file(filename, base_path, framework_paths, encoding_hints=None):
    filepath = get_filepath(filename, base_path, framework_paths)
    encoding, s = get_file_content(filepath, encoding_hints)
    return filepath, encoding, parse_string(s)
