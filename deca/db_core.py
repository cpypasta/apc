import os
import numpy as np

from deca.errors import *
from deca.ff_types import *
from deca.decompress import DecompressorOodleLZ
from deca.game_info import game_info_load
from deca.hashes import hash32_func, hash64_func
from deca.db_types import *
from deca.db_cross_game import DbCrossGame

dumped_cache_dir = False

language_codes = [
    'bra',  # Brazil
    'chi',  # Chinese
    'eng',  # English
    'fre',  # French
    'ger',  # German
    'ita',  # Italy
    'jap',  # Japanese
    'mex',  # Mexico
    'pol',  # Polish
    'rus',  # Russian
    'sch',  # Simplified Chinese
    'spa',  # Spanish
    'swe',  # Swedish
]


def format_hash32(v_hash):
    if v_hash is None:
        return v_hash
    return '{:08x}'.format(np.uint64(v_hash))


def format_hash48(v_hash):
    if v_hash is None:
        return v_hash
    return '{:012x}'.format(np.uint64(v_hash))


def format_hash64(v_hash):
    if v_hash is None:
        return v_hash
    return '{:016x}'.format(np.uint64(v_hash))


class VfsNode:
    __slots__ = (
        'uid',
        'v_hash',
        'v_path',
        'p_path',
        'file_type',
        'file_sub_type',
        'ext_hash',
        'content_hash',
        'magic',
        'pid',
        'index',
        'offset',
        'size_c',
        'size_u',
        '_blocks',
        'flags',
        'used_at_runtime_depth',
    )

    def __init__(
            self, uid=None, file_type=None,
            v_hash=None, p_path=None, v_path=None,
            pid=None, index=None,
            offset=None, size_c=None, size_u=None,
            file_sub_type=None, ext_hash=None,
            content_hash=None,
            magic=None,
            is_processed_file_raw_no_name=False,
            is_processed_file_raw_with_name=False,
            is_processed_file_type=False,
            is_processed_file_specific=False,
            is_temporary_file=False,
            compression_type=0,
            compression_flag=0,
            blocks=None,
            flags=None,
            used_at_runtime_depth=None,
            v_hash_type=node_flag_v_hash_type_4,
    ):
        self.uid = uid
        self.v_hash = v_hash
        self.v_path = v_path
        self.p_path = p_path
        self.file_type = file_type
        self.file_sub_type = file_sub_type
        self.ext_hash = ext_hash
        self.content_hash = content_hash
        self.magic = magic

        self.pid = pid
        self.index = index  # index in parent
        self.offset = offset  # offset in parent
        self.size_c = size_c  # compressed size in client
        self.size_u = size_u  # extracted size

        self._blocks = blocks

        if flags is None:
            self.flags = 0
            self.flags |= (compression_type << node_flag_compression_type_shift) & node_flag_compression_type_mask
            self.flags |= (compression_flag << node_flag_compression_flag_shift) & node_flag_compression_flag_mask
            if is_processed_file_raw_no_name:
                self.flags = self.flags | node_flag_processed_file_raw_no_name
            if is_processed_file_raw_with_name:
                self.flags = self.flags | node_flag_processed_file_raw_with_name
            if is_processed_file_type:
                self.flags = self.flags | node_flag_processed_file_type
            if is_processed_file_specific:
                self.flags = self.flags | node_flag_processed_file_specific
            if is_temporary_file:
                self.flags = self.flags | node_flag_temporary_file

            self.flags = (self.flags & ~node_flag_v_hash_type_mask) | v_hash_type

            # make sure type and flag was saved properly
            assert self.compression_type_get() == compression_type
            assert self.compression_flag_get() == compression_flag
        else:
            self.flags = flags

        self.used_at_runtime_depth = used_at_runtime_depth

    def flags_get(self, bit):
        return (self.flags & bit) == bit

    def flags_set_value(self, bit, value):
        if value:
            value = bit
        else:
            value = 0
        self.flags = (self.flags & ~bit) | value

    def flags_set(self, bit):
        self.flags_set_value(bit, True)

    def flags_clear(self, bit):
        self.flags_set_value(bit, False)

    def compression_type_get(self):
        return (self.flags & node_flag_compression_type_mask) >> node_flag_compression_type_shift

    def compression_type_set(self, value):
        self.flags = \
            (self.flags & ~node_flag_compression_type_mask) | \
            ((value << node_flag_compression_type_shift) & node_flag_compression_type_mask)

    def compression_flag_get(self):
        return (self.flags & node_flag_compression_flag_mask) >> node_flag_compression_flag_shift

    def compression_flag_set(self, value):
        self.flags = \
            (self.flags & ~node_flag_compression_flag_mask) | \
            ((value << node_flag_compression_flag_shift) & node_flag_compression_flag_mask)

    def temporary_file_get(self):
        return self.flags_get(node_flag_temporary_file)

    def temporary_file_set(self, value):
        self.flags_set_value(node_flag_temporary_file, value)

    def is_valid(self):
        return self.uid is not None and self.uid != 0

    def __str__(self):
        info = []
        if self.file_type is not None:
            info.append('ft:{}'.format(self.file_type))
        if self.v_hash is not None:
            info.append('h:{}'.format(self.v_hash_to_str()))
        if self.v_path is not None:
            info.append('v:{}'.format(self.v_path))
        if self.p_path is not None:
            info.append('p:{}'.format(self.p_path))
        if len(info) == 0:
            info.append('child({},{})'.format(self.pid, self.index))
        return ' '.join(info)

    def v_hash_to_str(self):
        hash_type = self.flags & node_flag_v_hash_type_mask
        if hash_type == node_flag_v_hash_type_4:
            return format_hash32(self.v_hash)
        elif hash_type == node_flag_v_hash_type_6:
            return format_hash48(self.v_hash)
        elif hash_type == node_flag_v_hash_type_8:
            return format_hash64(self.v_hash)
        else:
            raise NotImplementedError('hash_type not handled: {:016x}'.format(np.uint64(self.flags)))

    def blocks_raw(self):
        if not self._blocks:
            return None

        return self._blocks

    def blocks_get(self, vfs):
        vfs: VfsDatabase

        if self._blocks is None:
            self._blocks = vfs.blocks_where_node_id(self.uid)

            if self._blocks is None:
                self._blocks = False

        if not self._blocks:
            return [(self.offset, self.size_c, self.size_u)]

        return self._blocks


core_nodes_definition = \
    '''
    CREATE TABLE IF NOT EXISTS "core_nodes" (
        "node_id" INTEGER NOT NULL UNIQUE,
        "flags" INTEGER,
        "parent_id" INTEGER,
        "parent_index" INTEGER,
        "parent_offset" INTEGER,
        "v_hash" INTEGER,
        "v_path" TEXT,
        "p_path" TEXT,
        "content_hash" TEXT,
        "magic" INTEGER,
        "file_type" TEXT,
        "ext_hash" INTEGER,
        "size_c" INTEGER,
        "size_u" INTEGER,
        "file_sub_type" INTEGER,
        "used_at_runtime_depth" INTEGER,
        PRIMARY KEY("node_id")
    )
    '''

core_nodes_update_all_where_node_id = \
    """
    UPDATE core_nodes SET
    flags=(?),
    parent_id=(?),
    parent_index=(?),
    parent_offset=(?),
    v_hash=(?),
    v_path=(?),
    p_path=(?),
    content_hash=(?),
    magic=(?),
    file_type=(?),
    ext_hash=(?),
    size_c=(?),
    size_u=(?),
    file_sub_type=(?),
    used_at_runtime_depth=(?)
    WHERE node_id=(?)
    """

core_nodes_field_count = 16

core_nodes_all_fields = '(' + ','.join(['?'] * core_nodes_field_count) + ')'


def db_to_vfs_node(v):
    node = VfsNode(
        uid=v[0],
        flags=v[1],
        pid=v[2],
        index=v[3],
        offset=v[4],
        v_hash=v[5],
        v_path=to_bytes(v[6]),
        p_path=to_str(v[7]),
        content_hash=to_str(v[8]),
        magic=v[9],
        file_type=to_str(v[10]),
        ext_hash=v[11],
        size_c=v[12],
        size_u=v[13],
        file_sub_type=v[14],
        used_at_runtime_depth=v[15],
    )
    return node


def db_from_vfs_node(node: VfsNode):
    v = (
        node.uid,
        node.flags,
        node.pid,
        node.index,
        node.offset,
        node.v_hash,
        to_str(node.v_path),
        to_str(node.p_path),
        to_str(node.content_hash),
        node.magic,
        to_str(node.file_type),
        node.ext_hash,
        node.size_c,
        node.size_u,
        node.file_sub_type,
        node.used_at_runtime_depth,
    )
    return v


# string references
ref_flag_is_defined = 1 << 0
ref_flag_is_referenced = 1 << 1
ref_flag_is_file_name = 1 << 2
ref_flag_is_field_name = 1 << 3


class VfsDatabase(DbBase):
    def __init__(
            self, project_file, working_dir, logger,
            init_display=False,
            max_uncompressed_cache_size=(2 * 1024**3)
    ):
        super().__init__(os.path.join(working_dir, 'db', 'core.db'), logger)

        self.db_cg = DbCrossGame(os.path.abspath(os.path.join(working_dir, "..")), logger)

        self.project_file = project_file
        self.working_dir = working_dir
        self.game_info = game_info_load(project_file)
        self.decompress_oodle_lz = DecompressorOodleLZ(self.game_info.oo_decompress_dll)
        if 4 == self.game_info.file_hash_size:
            self.file_hash_db_id = 'hash32'
            self.file_hash = hash32_func
            self.file_hash_format = format_hash32
            self.file_hash_type = node_flag_v_hash_type_4
            self.ext_hash = hash32_func
        elif 8 == self.game_info.file_hash_size:
            self.file_hash_db_id = 'hash64'
            self.file_hash = hash64_func
            self.file_hash_format = format_hash64
            self.file_hash_type = node_flag_v_hash_type_8
            self.ext_hash = hash32_func
        else:
            raise NotImplementedError('File Hash Size of {} Not Implemented'.format(self.game_info.file_hash_size))

        os.makedirs(working_dir, exist_ok=True)

        if init_display:
            logger.log('OPENING: {} {}'.format(self.game_info.game_dir, working_dir))

        self._lookup_equipment_from_name = None
        self._lookup_equipment_from_hash = None
        self._lookup_translation_from_name = None
        self._lookup_note_from_file_path = None

        self.db_setup()

        # setup in memory uncompressed cache
        # self.uncompressed_cache_max_size = max_uncompressed_cache_size
        # self.uncompressed_cache_map = {}
        # self.uncompressed_cache_lru = []

    def hash_string_match(self, hash32=None, hash48=None, hash64=None, ext_hash32=None, string=None, to_dict=False):

        params = []
        wheres = []
        if hash32 is not None:
            if hash32 & 0xFFFFFFFF != hash32:
                return []
            params.append(hash32)
            wheres.append('(hash32 == (?))')

        if hash48 is not None:
            if hash48 & 0xFFFFFFFFFFFF != hash48:
                return []
            params.append(hash48)
            wheres.append('(hash48 == (?))')

        if hash64 is not None:
            params.append(hash64)
            wheres.append('(hash64 == (?))')

        if ext_hash32 is not None:
            if ext_hash32 & 0xFFFFFFFF != ext_hash32:
                return []
            params.append(ext_hash32)
            wheres.append('(ext_hash32 == (?))')

        if string is not None:
            string = to_str(string)
            params.append(string)
            wheres.append('(string == (?))')

        if len(wheres) > 0:
            where_str = ' WHERE ' + wheres[0]
            for ws in wheres[1:]:
                where_str = where_str + ' AND ' + ws
        else:
            where_str = ''

        if params:
            result = self.db_query_all(
                "SELECT rowid, string , hash32, hash48, hash64, ext_hash32 FROM core_strings " + where_str,
                params,
                dbg='hash_string_match'
            )
        else:
            result = self.db_query_all(
                "SELECT rowid, string , hash32, hash48, hash64, ext_hash32 FROM core_strings",
                dbg='hash_string_match_all'
            )

        if to_dict:
            result = [(r[0], (to_bytes(r[1]), r[2], r[3], r[4], r[5])) for r in result]
            result = dict(result)
        else:
            result = [(r[0], to_bytes(r[1]), r[2], r[3], r[4], r[5]) for r in result]

        return result
    def lookup_equipment_from_hash(self, name_hash):
        if self._lookup_equipment_from_hash is None:
            return None

        return self._lookup_equipment_from_hash.get(name_hash, None)
    def lookup_translation_from_name(self, name, default=None):
        if self._lookup_translation_from_name is None:
            return default

        return self._lookup_translation_from_name.get(name, default)


'''
--vfs-fs dropzone --vfs-archive patch_win64 --vfs-archive archives_win64 --vfs-fs .
'''

'''
tab/arc - file archive {hash, file}
aaf - compressed single file
sarc - file archive: {filename, hash, file}
avtx - directx image archives can contain multiple MIP levels
headerless-avtx - directx image archives with no header probably connected to avtx files can contain multiple MIP levels
adf - typed files with objects/type/...
'''
