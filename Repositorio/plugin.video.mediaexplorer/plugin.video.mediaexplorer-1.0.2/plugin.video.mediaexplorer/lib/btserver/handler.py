# -*- coding: utf-8 -*-
import BaseHTTPServer
import os
import re
import time
import types
import urllib
import urlparse

range_re = re.compile(r'bytes=(\d+)-')


def parse_range(ran):  # @ReservedAssignment
    if ran:
        m = range_re.match(ran)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass
    return 0


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, frm, *args):
        pass

    def do_GET(self):
        if self.server.request:
            self.server.request.wfile.close()
        self.server.request = self

        if self.do_HEAD():
            f = self.server.file.create_cursor(self.offset)
            while f == self.server.file.cursor:
                buf = f.read(1024)
                if buf:
                    try:
                        self.wfile.write(buf)
                    except Exception:
                        break
                else:
                    break
            f.close()

    def send_pls(self, files):
        playlist = "[playlist]\n\n"
        for x, f in enumerate(files):
            playlist += "File" + str(x + 1) + "=http://127.0.0.1:" + str(self.server._client.port) + "/" + urllib.quote(
                f.path) + "\n"
            playlist += "Title" + str(x + 1) + "=" + f.path + "\n"
        playlist += "NumberOfEntries=" + str(len(files))
        playlist += "Version=2"
        self.send_response(200, 'OK')
        self.send_header("Content-Length", str(len(playlist)))
        self.finish_header()
        self.wfile.write(playlist)

    def do_HEAD(self):
        url = urlparse.urlparse(self.path).path

        '''Whait to list of files '''
        while not self.server._client.files:
            time.sleep(1)

        files = self.server._client.files
        self.server.file = self.server._client.file

        '''Creates PLS playlist '''
        if url == "/playlist.pls":
            self.send_pls(files)
            return False

        '''Change File to download '''
        if not self.server.file or urllib.unquote(url) != '/' + self.server.file.path:
            fname = urllib.unquote(url)
            client = self.server._client
            for f in client.files:
                if fname == '/' + f.path:
                    client.set_file(f)
                    self.server.file = client.file
                    break

        while not self.server._client.has_meta:
            time.sleep(1)
        if self.server.file and urllib.unquote(url) == '/' + self.server.file.path:
            self.offset = 0
            size, mime = self._file_info()
            ran = parse_range(self.headers.get('Range', None))
            if ran:
                self.offset = ran
                ran = (ran, size - 1, size)

            self.send_resp_header(mime, size, ran)
            return True

        else:
            self.send_error(404, 'Not Found')

    def _file_info(self):
        size = self.server.file.size
        ext = os.path.splitext(self.server.file.path)[1]
        mime = self.server._client.video_exts.get(ext)
        if not mime:
            mime = 'application/octet-stream'
        return size, mime

    def send_resp_header(self, cont_type, cont_length, ran=None):  # @ReservedAssignment
        if ran:
            self.send_response(206, 'Partial Content')
        else:
            self.send_response(200, 'OK')

        self.send_header('Content-Type', cont_type)
        self.send_header('transferMode.dlna.org', 'Streaming')
        self.send_header('contentFeatures.dlna.org',
                         'DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01700000000000000000000000000000')
        self.send_header('Accept-Ranges', 'bytes')

        if ran:
            if isinstance(ran, (types.TupleType, types.ListType)) and len(ran) == 3:
                self.send_header('Content-Range', 'bytes %d-%d/%d' % ran)
                self.send_header('Content-Length', ran[1] - ran[0] + 1)
            else:
                raise ValueError('Invalid range value')
        else:
            self.send_header('Content-Length', cont_length)
        self.finish_header()

    def finish_header(self):
        self.send_header('Connection', 'close')
        self.end_headers()
