__author__ = 'Jeff'
import pickle

def create_offsets(read_path, write_path):
    line_offset = []
    offset = 0
    for line in file.open(read_path):
        line_offset.append(offset)
        offset += len(line)
    return pickle.dump(line_offset, open(write_path, 'w'))
