#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate strings for all the date formats.

Author: Gertjan van den Burg

"""


def main():
    year2 = "YY"
    year4 = "YYYY"
    month_leading = "MM"
    month_sparse = "M"
    day_leading = "D"
    day_leading = "DD"
    day_sparse = "D"
    sep = "x"
    pats = []
    for year in [year2, year4]:
        for month in [month_leading, month_sparse]:
            for day in [day_leading, day_sparse]:
                fmt = dict(year=year, month=month, day=day, sep=sep)
                pats.append("{year}{sep}{month}{sep}{day}".format(**fmt))
                pats.append("{day}{sep}{month}{sep}{year}".format(**fmt))
                pats.append("{month}{sep}{day}{sep}{year}".format(**fmt))
                pats.append("{year}年{month}月{day}日".format(**fmt))
                pats.append("{year}년{month}월{day}일".format(**fmt))

    for year in [year2, year4]:
        fmt = dict(year=year, month=month_leading, day=day_leading, sep="")
        pats.append("{year}{sep}{month}{sep}{day}".format(**fmt))
        pats.append("{day}{sep}{month}{sep}{year}".format(**fmt))
        pats.append("{month}{sep}{day}{sep}{year}".format(**fmt))

    for pat in sorted(pats):
        print(pat)


if __name__ == "__main__":
    main()
