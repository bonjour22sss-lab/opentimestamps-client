import io
import os
from opentimestamps.core.timestamp import DetachedTimestampFile
from opentimestamps.core.op import OpSHA256, OpAppend
from opentimestamps.core.serialize import StreamSerializationContext
from otsclient.cmds import create_timestamp

class MockArgs:
    def __init__(self):
        self.calendar_urls = [
            'https://a.pool.opentimestamps.org',
            'https://b.pool.opentimestamps.org',
            'https://a.pool.eternitywall.com',
            'https://ots.btc.catallaxy.com'
        ]
        self.m = 1
        self.timeout = 10
        self.use_btc_wallet = False
        self.wait = False
        self.cache = {}

def stamp_data(data_bytes):
    fd = io.BytesIO(data_bytes)
    file_timestamp = DetachedTimestampFile.from_fd(OpSHA256(), fd)

    # Add nonce for privacy as per ots client standard
    nonce = os.urandom(16)
    nonce_appended_stamp = file_timestamp.timestamp.ops.add(OpAppend(nonce))
    merkle_root = nonce_appended_stamp.ops.add(OpSHA256())

    args = MockArgs()
    create_timestamp(merkle_root, args.calendar_urls, args)

    # Serialize
    out = io.BytesIO()
    ctx = StreamSerializationContext(out)
    file_timestamp.serialize(ctx)
    return out.getvalue()
