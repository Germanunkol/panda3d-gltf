import json
import struct


def is_glb_file(filepath):
    with open(filepath, 'rb') as glbfile:
        if glbfile.read(4) == b'glTF':
            return True
        else:
            return False


def read_glb_file(filepath):
    def read_glb_chunk(glbfile):
        chunk_size, = struct.unpack('<I', glbfile.read(4))
        chunk_type = glbfile.read(4)
        chunk_data = glbfile.read(chunk_size)
        return chunk_type, chunk_data

    with open(filepath, 'rb') as glbfile:
        if glbfile.read(4) != b'glTF':
            raise RuntimeError('attempted to load non-glb file as glb')

        version, = struct.unpack('<I', glbfile.read(4))
        if version != 2:
            raise RuntimeError(
                f'Only GLB version 2 is supported, file is version {version}'
            )

        length, = struct.unpack('<I', glbfile.read(4))

        chunk_type, chunk_data = read_glb_chunk(glbfile)
        assert chunk_type == b'JSON'
        gltf_data = json.loads(chunk_data.decode('utf-8'))

        if glbfile.tell() < length:
            chunk_type, chunk_data = read_glb_chunk(glbfile)
            assert chunk_type == b'BIN\000'
            if not 'buffers' not in gltf_data:
                gltf_data['buffers'] = []
            gltf_data['buffers'].insert(0, {
                'uri': '_glb_bin',
                '_glb_bin': chunk_data,
            })

    return gltf_data


def read_gltf_file(filepath):
    if is_glb_file(filepath):
        return read_glb_file(filepath)
    else:
        with open(filepath) as gltffile:
            return json.load(gltffile)
