import lzma
import pickle

from namedtuples import CihaiT

with lzma.open("unihan_data.pickle.xz") as f:
    unihan = pickle.load(f)
