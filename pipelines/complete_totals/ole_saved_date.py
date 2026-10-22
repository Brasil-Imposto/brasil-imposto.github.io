"""Read the 'last saved' and 'created' timestamps of a legacy .xls (OLE2 compound file) from its SummaryInformation stream.

Usage: python3 ole_saved_date.py <file.xls>
Only standard library. Prints ISO dates (UTC). This is file metadata written by the author's software, not a publication date.
"""
import datetime
import struct
import sys


def read_stream(data, name):
    sector_size = 1 << struct.unpack_from("<H", data, 30)[0]
    mini_size = 1 << struct.unpack_from("<H", data, 32)[0]
    num_fat, first_dir, _, mini_cutoff, first_minifat, num_minifat, first_difat, num_difat = struct.unpack_from("<IIIIIIII", data, 44)
    difat = list(struct.unpack_from("<109I", data, 76))
    nxt = first_difat
    while nxt not in (0xFFFFFFFE, 0xFFFFFFFF) and num_difat:
        off = 512 + nxt * sector_size
        vals = struct.unpack_from(f"<{sector_size // 4}I", data, off)
        difat += vals[:-1]
        nxt = vals[-1]
        num_difat -= 1
    fat = []
    for s in difat[:num_fat]:
        fat += struct.unpack_from(f"<{sector_size // 4}I", data, 512 + s * sector_size)

    def chain(start):
        out = b""
        while start not in (0xFFFFFFFE, 0xFFFFFFFF):
            out += data[512 + start * sector_size: 512 + (start + 1) * sector_size]
            start = fat[start]
        return out

    directory = chain(first_dir)
    entries = []
    for i in range(0, len(directory), 128):
        e = directory[i:i + 128]
        nlen = struct.unpack_from("<H", e, 64)[0]
        ename = e[:max(nlen - 2, 0)].decode("utf-16-le")
        start, size = struct.unpack_from("<IQ", e, 116)
        entries.append((ename, start, size))
    root = entries[0]
    for ename, start, size in entries:
        if ename == name:
            if size < mini_cutoff:
                ministream = chain(root[1])
                minifat = struct.unpack(f"<{len(chain(first_minifat)) // 4}I", chain(first_minifat))
                out = b""
                while start not in (0xFFFFFFFE, 0xFFFFFFFF):
                    out += ministream[start * mini_size:(start + 1) * mini_size]
                    start = minifat[start]
                return out[:size]
            return chain(start)[:size]
    raise KeyError(name)


def filetime(value):
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=value // 10)).isoformat()


def main():
    data = open(sys.argv[1], "rb").read()
    stream = read_stream(data, "\x05SummaryInformation")
    section_offset = struct.unpack_from("<I", stream, 44)[0]
    count = struct.unpack_from("<I", stream, section_offset + 4)[0]
    names = {12: "created", 13: "last_saved", 11: "last_printed"}
    for k in range(count):
        pid, off = struct.unpack_from("<II", stream, section_offset + 8 + 8 * k)
        if pid in names:
            vtype = struct.unpack_from("<I", stream, section_offset + off)[0]
            if vtype == 64:
                print(names[pid], filetime(struct.unpack_from("<Q", stream, section_offset + off + 4)[0]))


if __name__ == "__main__":
    main()
