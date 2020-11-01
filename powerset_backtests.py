# 
# 11.01.2020

import pandas as pd
from itertools import chain, combinations


def indicator_powerset(indicators):
    s = list(indicators)
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def retrieve_sptickers():
    sp_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return list(sp_table[0]['Symbol'])


if __name__ == '__main__':
    