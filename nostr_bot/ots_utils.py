import io
import os
import binascii
from opentimestamps.core.timestamp import Timestamp, DetachedTimestampFile
from opentimestamps.core.op import OpSHA256, OpAppend
from opentimestamps.core.serialize import StreamSerializationContext, StreamDeserializationContext
from otsclient.cmds import create_timestamp, upgrade_timestamp, is_timestamp_complete

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
        self.cache = {} # Should probably use a real cache if possible

def _stamp_core(file_timestamp):
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

def stamp_event_id(event_id_hex):
    event_id_bin = binascii.unhexlify(event_id_hex)
    file_timestamp = DetachedTimestampFile(OpSHA256(), Timestamp(event_id_bin))
    ots_bin = _stamp_core(file_timestamp)
    return binascii.hexlify(ots_bin).decode('utf-8')

def stamp_data(data_bytes):
    fd = io.BytesIO(data_bytes)
    file_timestamp = DetachedTimestampFile.from_fd(OpSHA256(), fd)
    return _stamp_core(file_timestamp)

def upgrade_ots_data(ots_data_hex):
    ots_data_bin = binascii.unhexlify(ots_data_hex)
    fd = io.BytesIO(ots_data_bin)
    ctx = StreamDeserializationContext(fd)
    detached_timestamp = DetachedTimestampFile.deserialize(ctx)

    args = MockArgs()
    # In a real app we might want a persistent cache
    args.cache = {}

    changed = upgrade_timestamp(detached_timestamp.timestamp, args)

    if changed:
        out = io.BytesIO()
        ctx = StreamSerializationContext(out)
        detached_timestamp.serialize(ctx)
        return binascii.hexlify(out.getvalue()).decode('utf-8'), is_timestamp_complete(detached_timestamp.timestamp, args)

    return None, is_timestamp_complete(detached_timestamp.timestamp, args)

def is_complete(ots_data_hex):
    ots_data_bin = binascii.unhexlify(ots_data_hex)
    fd = io.BytesIO(ots_data_bin)
    ctx = StreamDeserializationContext(fd)
    detached_timestamp = DetachedTimestampFile.deserialize(ctx)
    return is_timestamp_complete(detached_timestamp.timestamp, MockArgs())
