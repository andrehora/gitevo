from datetime import date
from gitevo.utils import DateUtils

def test_date_range_year():
    DateUtils.date_unit = 'year'
    assert len(DateUtils.date_range(date(2000,1,1), date(2000,1,1))) == 1
    assert len(DateUtils.date_range(date(2000,1,1), date(2000,12,1))) == 1
    assert len(DateUtils.date_range(date(2000,1,1), date(2001,1,1))) == 2
    assert len(DateUtils.date_range(date(2000,1,1), date(2010,1,1))) == 11

def test_date_range_month_same_year():
    DateUtils.date_unit = 'month'
    assert len(DateUtils.date_range(date(2000,1,1), date(2000,1,1))) == 1
    assert len(DateUtils.date_range(date(2000,1,1), date(2000,7,1))) == 7
    assert len(DateUtils.date_range(date(2000,1,1), date(2000,12,1))) == 12

def test_date_range_month_distinct_years():
    DateUtils.date_unit = 'month'
    assert len(DateUtils.date_range(date(2000,1,1), date(2001,1,1))) == 13
    assert len(DateUtils.date_range(date(2000,1,1), date(2001,12,1))) == 24

    assert len(DateUtils.date_range(date(2000,1,1), date(2002,6,1))) == 30
    assert len(DateUtils.date_range(date(2000,1,1), date(2002,12,1))) == 36

def test_formatted_dates_year():
    DateUtils.date_unit = 'year'

    dates = DateUtils.date_range(date(2000,1,1), date(2000,1,1))
    assert DateUtils.formatted_dates(dates) == ['2000']

    dates = DateUtils.date_range(date(2000,1,1), date(2000,12,1))
    assert DateUtils.formatted_dates(dates) == ['2000']

    dates = DateUtils.date_range(date(2000,1,1), date(2001,1,1))
    assert DateUtils.formatted_dates(dates) == ['2000', '2001']

    dates = DateUtils.date_range(date(2000,1,1), date(2005,1,1))
    assert DateUtils.formatted_dates(dates) == ['2000', '2001', '2002', '2003', '2004', '2005']

def test_formatted_dates_month():
    DateUtils.date_unit = 'month'

    dates = DateUtils.date_range(date(2000,1,1), date(2000,1,1))
    assert DateUtils.formatted_dates(dates) == ['01/2000']

    dates = DateUtils.date_range(date(2000,1,1), date(2000,2,1))
    assert DateUtils.formatted_dates(dates) == ['01/2000', '02/2000']

    dates = DateUtils.date_range(date(2000,1,1), date(2001,4,1))
    assert DateUtils.formatted_dates(dates) == ['01/2000', '02/2000', '03/2000', '04/2000', 
                                                '05/2000', '06/2000', '07/2000', '08/2000', 
                                                '09/2000', '10/2000', '11/2000', '12/2000', 
                                                '01/2001', '02/2001', '03/2001', '04/2001']