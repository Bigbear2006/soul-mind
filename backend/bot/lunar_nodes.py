from datetime import datetime

lunar_nodes = {
    (datetime(1949, 8, 3), datetime(1951, 2, 27)): {
        'north': 'Aries',
        'south': 'Libra',
    },
    (datetime(1951, 2, 28), datetime(1952, 8, 20)): {
        'north': 'Pisces',
        'south': 'Virgo',
    },
    (datetime(1952, 8, 21), datetime(1954, 3, 11)): {
        'north': 'Aquarius',
        'south': 'Leo',
    },
    (datetime(1954, 3, 12), datetime(1955, 10, 2)): {
        'north': 'Capricorn',
        'south': 'Cancer',
    },
    (datetime(1955, 10, 3), datetime(1957, 4, 23)): {
        'north': 'Sagittarius',
        'south': 'Gemini',
    },
    (datetime(1957, 4, 24), datetime(1958, 11, 15)): {
        'north': 'Scorpio',
        'south': 'Taurus',
    },
    (datetime(1958, 11, 16), datetime(1960, 6, 8)): {
        'north': 'Libra',
        'south': 'Aries',
    },
    (datetime(1960, 6, 9), datetime(1961, 12, 29)): {
        'north': 'Virgo',
        'south': 'Pisces',
    },
    (datetime(1961, 12, 30), datetime(1963, 7, 23)): {
        'north': 'Leo',
        'south': 'Aquarius',
    },
    (datetime(1963, 7, 24), datetime(1965, 2, 14)): {
        'north': 'Cancer',
        'south': 'Capricorn',
    },
    (datetime(1965, 2, 15), datetime(1966, 9, 5)): {
        'north': 'Gemini',
        'south': 'Sagittarius',
    },
    (datetime(1966, 9, 6), datetime(1968, 3, 28)): {
        'north': 'Taurus',
        'south': 'Scorpio',
    },
    (datetime(1968, 3, 29), datetime(1969, 10, 19)): {
        'north': 'Aries',
        'south': 'Libra',
    },
    (datetime(1969, 10, 20), datetime(1971, 5, 11)): {
        'north': 'Pisces',
        'south': 'Virgo',
    },
    (datetime(1971, 5, 12), datetime(1972, 12, 2)): {
        'north': 'Aquarius',
        'south': 'Leo',
    },
    (datetime(1972, 12, 3), datetime(1974, 6, 25)): {
        'north': 'Capricorn',
        'south': 'Cancer',
    },
    (datetime(1974, 6, 26), datetime(1976, 1, 17)): {
        'north': 'Sagittarius',
        'south': 'Gemini',
    },
    (datetime(1976, 1, 18), datetime(1977, 8, 8)): {
        'north': 'Scorpio',
        'south': 'Taurus',
    },
    (datetime(1977, 8, 9), datetime(1979, 4, 1)): {
        'north': 'Libra',
        'south': 'Aries',
    },
    (datetime(1979, 4, 2), datetime(1980, 10, 23)): {
        'north': 'Virgo',
        'south': 'Pisces',
    },
    (datetime(1980, 10, 24), datetime(1982, 5, 13)): {
        'north': 'Leo',
        'south': 'Aquarius',
    },
    (datetime(1982, 5, 14), datetime(1983, 12, 7)): {
        'north': 'Cancer',
        'south': 'Capricorn',
    },
    (datetime(1983, 12, 8), datetime(1985, 5, 30)): {
        'north': 'Gemini',
        'south': 'Sagittarius',
    },
    (datetime(1985, 5, 31), datetime(1986, 12, 21)): {
        'north': 'Taurus',
        'south': 'Scorpio',
    },
    (datetime(1986, 12, 22), datetime(1988, 7, 12)): {
        'north': 'Aries',
        'south': 'Libra',
    },
    (datetime(1988, 7, 13), datetime(1990, 2, 3)): {
        'north': 'Pisces',
        'south': 'Virgo',
    },
    (datetime(1990, 2, 4), datetime(1991, 8, 26)): {
        'north': 'Aquarius',
        'south': 'Leo',
    },
    (datetime(1991, 8, 27), datetime(1993, 3, 20)): {
        'north': 'Capricorn',
        'south': 'Cancer',
    },
    (datetime(1993, 3, 21), datetime(1994, 10, 11)): {
        'north': 'Sagittarius',
        'south': 'Gemini',
    },
    (datetime(1994, 10, 12), datetime(1996, 5, 1)): {
        'north': 'Scorpio',
        'south': 'Taurus',
    },
    (datetime(1996, 5, 2), datetime(1997, 11, 24)): {
        'north': 'Libra',
        'south': 'Aries',
    },
    (datetime(1997, 11, 25), datetime(1999, 8, 21)): {
        'north': 'Virgo',
        'south': 'Pisces',
    },
    (datetime(1999, 8, 22), datetime(2001, 4, 9)): {
        'north': 'Leo',
        'south': 'Aquarius',
    },
    (datetime(2001, 4, 10), datetime(2002, 10, 13)): {
        'north': 'Cancer',
        'south': 'Capricorn',
    },
    (datetime(2002, 10, 14), datetime(2004, 5, 5)): {
        'north': 'Gemini',
        'south': 'Sagittarius',
    },
    (datetime(2004, 5, 6), datetime(2005, 12, 22)): {
        'north': 'Taurus',
        'south': 'Scorpio',
    },
    (datetime(2005, 12, 23), datetime(2007, 6, 19)): {
        'north': 'Aries',
        'south': 'Libra',
    },
    (datetime(2007, 6, 20), datetime(2009, 1, 8)): {
        'north': 'Pisces',
        'south': 'Virgo',
    },
    (datetime(2009, 1, 9), datetime(2010, 8, 21)): {
        'north': 'Aquarius',
        'south': 'Leo',
    },
    (datetime(2010, 8, 22), datetime(2012, 3, 3)): {
        'north': 'Capricorn',
        'south': 'Cancer',
    },
    (datetime(2012, 3, 4), datetime(2013, 8, 22)): {
        'north': 'Sagittarius',
        'south': 'Gemini',
    },
    (datetime(2013, 8, 23), datetime(2015, 11, 11)): {
        'north': 'Scorpio',
        'south': 'Taurus',
    },
    (datetime(2015, 11, 12), datetime(2017, 5, 9)): {
        'north': 'Libra',
        'south': 'Aries',
    },
    (datetime(2017, 5, 10), datetime(2018, 11, 5)): {
        'north': 'Virgo',
        'south': 'Pisces',
    },
    (datetime(2018, 11, 6), datetime(2020, 5, 4)): {
        'north': 'Leo',
        'south': 'Aquarius',
    },
    (datetime(2020, 5, 5), datetime(2022, 1, 18)): {
        'north': 'Cancer',
        'south': 'Capricorn',
    },
    (datetime(2022, 1, 19), datetime(2023, 7, 17)): {
        'north': 'Gemini',
        'south': 'Sagittarius',
    },
    (datetime(2023, 7, 18), datetime(2025, 1, 11)): {
        'north': 'Taurus',
        'south': 'Scorpio',
    },
    (datetime(2025, 1, 12), datetime(2026, 7, 26)): {
        'north': 'Aries',
        'south': 'Libra',
    },
    (datetime(2026, 7, 27), datetime(2028, 3, 23)): {
        'north': 'Pisces',
        'south': 'Virgo',
    },
    (datetime(2028, 3, 24), datetime(2029, 9, 18)): {
        'north': 'Aquarius',
        'south': 'Leo',
    },
    (datetime(2029, 9, 19), datetime(2031, 4, 14)): {
        'north': 'Capricorn',
        'south': 'Cancer',
    },
}


def get_lunar_nodes(date: datetime = None) -> dict[str, str] | None:
    if date is None:
        date = datetime.now()
    for date_range, nodes in lunar_nodes.items():
        start_date, end_date = date_range
        if start_date <= date <= end_date:
            return nodes
    return None
