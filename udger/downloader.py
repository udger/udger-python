import os

from .base import cached_property
from .base import UdgerBase

import gzip
import io
import struct
import tempfile
import urllib.request

class UdgerDownloader(object):

    udger_data_file = 'udgerdb_v3.dat.gz'
    download_url = 'http://data.udger.com/'

    def __init__(self, client_key, data_dir=None):
        self.client_key = client_key
        self.data_dir = data_dir or tempfile.gettempdir()

    def download(self):
        url = UdgerDownloader.download_url + self.client_key + '/' + UdgerDownloader.udger_data_file
        response = urllib.request.urlopen(url)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)

        with open(self.new_filename, 'wb') as outfile:
            outfile.write(decompressed_file.read())
        os.rename(self.new_filename, os.path.join(self.data_dir, UdgerBase.db_filename))

    @cached_property
    def new_filename(self):
        return os.path.join(self.data_dir, UdgerBase.db_filename + '.new')
