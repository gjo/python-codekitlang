# -*- coding: utf-8 -*-

import collections
import logging
import os
import re


Fragment = collections.namedtuple(
    'Fragment',
    (
        'pos',  # fpos of fragment start
        'line',  # line number of fragment
        'column',  # column number of fragment
        'command',  # NOOP, STOR, LOAD, JUMP
        'args',
    ),
)
NEW_LINE_RE = re.compile(r'\r?\n', re.MULTILINE)
SPECIAL_COMMENT_RE = re.compile(
    r'(?P<wrapper><!--\s*(?:'
    r'@(?:(?i)(?:import|include))\s+(?P<filenames>.*?)'
    r'|'
    r'[@$](?P<variable>[a-zA-Z][^\s:=]*)\s*(?:[\s:=]\s*(?P<value>.*?))?'
    r')-->)',
    re.DOTALL | re.LOCALE | re.MULTILINE | re.UNICODE
)
logger = logging.getLogger(__name__)


def get_file_content(filepath, encoding_hints=None):
    """
    @type filepath: str
    @type encoding_hints: [str, ...]
    @rtype: (str, str)
    """
    with open(filepath, 'rb') as fp:
        b = fp.read()
    # TODO: not implemented encoding detection yet
    return 'utf-8', unicode(b, encoding='utf-8', errors='replace')


class CompileError(Exception):
    pass


class FileNotFoundError(CompileError):
    pass


class UnknownEncodingError(CompileError):
    pass


class VariableNotFoundError(CompileError):
    pass


class Compiler(object):

    NEW_LINE_RE = NEW_LINE_RE
    SPECIAL_COMMENT_RE = SPECIAL_COMMENT_RE

    def __init__(self, framework_paths=None):
        """
        @param framework_paths: [str, ...]
        """
        if framework_paths is None:
            self.framework_paths = tuple()
        elif isinstance(framework_paths, tuple):
            self.framework_paths = framework_paths
        elif isinstance(framework_paths, basestring):
            self.framework_paths = (framework_paths,)
        else:
            self.framework_paths = tuple(framework_paths)
        self.parsed_caches = dict()

    def resolve_path(self, filename, base_path):
        """
        @type filename: str
        @type base_path: str
        @rtype: str
        """
        _, ext = os.path.splitext(filename)
        if not ext:
            filename += '.kit'
            ext = '.kit'
        if ext == '.kit':
            prefixes = ('', '_')
            paths = (base_path,) + self.framework_paths
        else:
            prefixes = ('',)
            paths = (base_path,)
        for prefix in prefixes:
            for path in paths:
                filepath = os.path.realpath(os.path.join(path, filename))
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

    def normalize_path(self, filepath=None, filename=None, basepath=None):
        if filepath:
            filepath = os.path.realpath(filepath)
        elif filename and basepath:
            filepath = self.resolve_path(filename, basepath)
        else:
            pass  # TODO: handle assert
        return filepath

    def get_new_signature(self, filepath):
        """
        @param filepath: `realpath`ed full path of file
        @type filepath: str
        @return: tuple of inode number, mtime and size
        @rtye: (int, int, int) or None
        """
        cached_signature = None
        if filepath in self.parsed_caches:
            cache = self.parsed_caches[filepath]
            cached_signature = cache['signature']
        stat = os.stat(filepath)
        signature = stat.st_ino, stat.st_mtime, stat.st_size
        if cached_signature and signature == cached_signature:
            signature = None
        return signature

    def parse_str(self, s):
        """
        @type s: str
        @rtype: [(int, int, int, str, str), ...]
        """
        parsed = []
        pos = 0
        line = 1
        column = 1
        for m in self.SPECIAL_COMMENT_RE.finditer(s):
            if m.start('wrapper') > pos:
                subs = s[pos:m.start('wrapper')]
                parsed.append(Fragment(pos, line, column, 'NOOP', subs))

            pos = m.start('wrapper')
            subs = self.NEW_LINE_RE.split(s[:pos])
            line = len(subs)
            column = len(subs[-1]) + 1

            if m.group('filenames'):
                for filename in m.group('filenames').split(','):
                    filename = filename.strip().strip('\'"')
                    parsed.append(Fragment(pos, line, column, 'JUMP',
                                           filename))
            elif m.group('value'):
                value = m.group('value').strip()
                parsed.append(Fragment(pos, line, column, 'STOR',
                                       (m.group('variable'), value)))
            else:  # m.group('variable')
                parsed.append(Fragment(pos, line, column, 'LOAD',
                                       m.group('variable')))

            pos = m.end('wrapper')
            subs = self.NEW_LINE_RE.split(s[:pos])
            line = len(subs)
            column = len(subs[-1]) + 1

        parsed.append(Fragment(pos, line, column, 'NOOP', s[pos:]))
        return parsed

    def parse_file(self, filepath=None, filename=None, basepath=None):
        filepath = self.normalize_path(filepath, filename, basepath)
        signature = self.get_new_signature(filepath)
        if signature:
            _, ext = os.path.splitext(filepath)
            encoding, s = get_file_content(filepath)
            if ext == '.kit':
                data = self.parse_str(s)
            else:
                data = [Fragment(0, 1, 1, 'NOOP', s)]
            self.parsed_caches[filepath] = dict(
                signature=signature,
                encoding=encoding,
                data=data,
            )
            for i in range(len(data)):
                fragment = data[i]
                if fragment.command == 'JUMP':
                    subfilepath = self.parse_file(
                        filename=fragment.args,
                        basepath=os.path.dirname(filepath)
                    )
                    data[i] = Fragment(fragment.pos,
                                       fragment.line,
                                       fragment.column,
                                       'JUMP',
                                       subfilepath)
        return filepath

    def generate_to_list(self, filepath, context=None):
        filepath = os.path.realpath(filepath)
        if context is None:
            context = dict()
        compiled = []
        if filepath not in self.parsed_caches:
            filepath = self.parse_file(filepath=filepath)
        cache = self.parsed_caches[filepath]
        for fragment in cache['data']:
            if fragment.command == 'NOOP':
                compiled.append(fragment.args)
            elif fragment.command == 'STOR':
                context[fragment.args[0]] = fragment.args[1]
            elif fragment.command == 'LOAD':
                compiled.append(context.get(fragment.args, ''))
            elif fragment.command == 'JUMP':
                compiled.extend(
                    self.generate_to_list(fragment.args, context.copy())
                )
        return compiled

    def generate_to_str(self, filepath):
        return ''.join(self.generate_to_list(filepath))

    def generate_to_file(self, dest, src):
        dest = os.path.realpath(dest)
        d = os.path.dirname(dest)
        if not os.path.exists(d):
            os.makedirs(d)
        s = self.generate_to_str(src)
        # TODO: not implemented encoding detection yet
        s = s.encode('utf-8')
        with open(dest, 'wb') as fp:
            fp.write(s)
        return
