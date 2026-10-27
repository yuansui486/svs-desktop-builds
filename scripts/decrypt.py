"""Decrypt and safely extract a maintainer-created source snapshot."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b'SVS-SOURCE-1\0'
source, destination = map(Path, sys.argv[1:])
manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
if manifest['build_id'] != os.environ['BUILD_ID']:
    raise ValueError('Build input ID mismatch')
archive = source / 'source.enc'
with archive.open('rb') as stream:
    if hashlib.file_digest(stream, 'sha256').hexdigest() != manifest['sha256']:
        raise ValueError('Encrypted input SHA256 mismatch')
key = base64.b64decode(os.environ.pop('SVS_SOURCE_KEY'), validate=True)
if len(key) != 32:
    raise ValueError('Missing or invalid source key')
plain = source / 'source.tar.gz'
try:
    with archive.open('rb') as encrypted, plain.open('wb') as output:
        if encrypted.read(len(MAGIC)) != MAGIC:
            raise ValueError('Unknown input format')
        nonce = encrypted.read(12)
        encrypted.seek(-16, 2)
        tag = encrypted.read(16)
        remaining = encrypted.tell() - len(MAGIC) - 12 - 16
        encrypted.seek(len(MAGIC) + 12)
        decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
        decryptor.authenticate_additional_data(MAGIC)
        while remaining:
            block = encrypted.read(min(1024 * 1024, remaining))
            if not block:
                raise ValueError('Truncated input')
            output.write(decryptor.update(block))
            remaining -= len(block)
        output.write(decryptor.finalize())
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(plain, 'r:gz') as tar:
        members = tar.getmembers()
        seen = set()
        for member in members:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or '\\' in member.name or ':' in member.name or member.name in seen:
                raise ValueError('Unsafe source archive member')
            seen.add(member.name)
        for member in members:
            path = destination / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as input_stream, path.open('wb') as output:
                while block := input_stream.read(1024 * 1024):
                    output.write(block)
            path.chmod(member.mode & 0o777)
    print(f'Authenticated source snapshot: {len(members)} files')
finally:
    plain.unlink(missing_ok=True)
