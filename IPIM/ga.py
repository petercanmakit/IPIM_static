"""A wapper for Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import config as cfg

# GA Configuration
SCOPES = cfg.ga_config['SCOPES']
KEY_FILE_LOCATION = cfg.ga_config['KEY_FILE_LOCATION']
VIEW_ID = cfg.ga_config['VIEW_ID']

def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
        An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analytics', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, startdate_str='2017-01-01', enddate_str='today', bywhat='total'):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        startdate_str, enddate_str: '2017-01-01', 'today', 'NdaysAgo'
        bywhat: 'total', 'day', 'week', 'month', 'year'
    Returns:
        The Analytics Reporting API V4 response.
    """
    dimension_array = []
    if bywhat == 'day':
        dimension_array = [{'name': 'ga:year'}, {'name': 'ga:month'}, {'name': 'ga:day'}]
    elif bywhat == 'week':
        dimension_array = [{'name': 'ga:year'}, {'name': 'ga:week'}]
    elif bywhat == 'month':
        dimension_array = [{'name': 'ga:year'}, {'name': 'ga:month'}]
    elif bywhat == 'year' :
        dimension_array = [{'name': 'ga:year'}]
    else: # bywhat == 'total'
        dimension_array = []

    return analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': startdate_str, 'endDate': enddate_str}],
                    'metrics': [{'expression': 'ga:sessions'}] ,
                    'dimensions': dimension_array,
                    "includeEmptyRows": True
                }]
            }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
        response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        # print report
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])
            print dimensions
            print dateRangeValues

            for header, dimension in zip(dimensionHeaders, dimensions):
                print header + ': ' + dimension

            for i, values in enumerate(dateRangeValues):
                # print 'Date range: ' + str(i)
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                  #if metricHeader.get('name') == 'ga:sessions':
                  print "value: " + value

def get_pageviews(response):
    """parse response, get the pageviews # array

    Args:
        response: An Analytics Reporting API V4 response.
    Returns:
        [label array<str>, pageviews array<int>]
    """
    label_array = []
    pageviews_array = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            # generate one label
            labelstr = ""
            i = 0
            for ele in dimensions:
                i += 1
                if i != len(dimensions):
                    labelstr += (str(ele) + "-")
                else :
                    labelstr += str(ele)
            label_array.append(str(labelstr))
            # generate one pageviews
            pageviewsint = 0
            for ele in dateRangeValues:
                pageviewsint = int(ele[u'values'][0])
            pageviews_array.append(pageviewsint)
    return [label_array, pageviews_array]

def get_pageviews_array(analytics, startdate_str='2017-01-01', enddate_str='today', bywhat='total'):
    """get the pageviews # array

    Args:
        analytics: an initialized analytics object,
        startdate_str='2017-01-01',
        enddate_str='today',
        bywhat='total' or 'day' or 'week' or 'month' or 'year'
    Returns:
        [label array<str>, pageviews array<int>]
    """
    response = get_report(analytics, startdate_str, enddate_str, bywhat)
    return get_pageviews(response)

def get_social_report(analytics):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
        The Analytics Reporting API V4 response.
    """
    dimension_array = [{'name': 'ga:socialInteractionNetworkAction'}]

    return analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': '2017-05-01', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:socialInteractions'}] ,
                    'dimensions': dimension_array,
                    "includeEmptyRows": True
                }]
            }
    ).execute()

def get_socialclicks(response):
    """parse response, get the socialclicks # array

    Args:
        response: An Analytics Reporting API V4 response.
    Returns:
        [label array<str>, socialclicks array<int>]
    """
    label_array = []
    socialclicks_array = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            # generate one label
            labelstr = ""
            for ele in dimensions:
                labelstr = str(ele)
            label_array.append(str(labelstr))
            # generate one pageviews
            socialclicksint = 0
            for ele in dateRangeValues:
                socialclicksint = int(ele[u'values'][0])
            socialclicks_array.append(socialclicksint)

    new_label_array = []
    new_socialclicks_array = []
    facebook = 0
    for i in range(len(label_array)):
        if label_array[i].startswith('Facebook :'):
            facebook += socialclicks_array[i]
        else :
            new_label_array.append(label_array[i].replace(' ','').split(':')[0])
            new_socialclicks_array.append(socialclicks_array[i])
    if facebook > 0:
        new_label_array.append('Facebook')
        new_socialclicks_array.append(facebook)
    return [new_label_array, new_socialclicks_array]

def get_socialclicks_array(analytics):
    """get the pageviews # array

    Args:
        analytics: an initialized analytics object,
        startdate_str='2017-01-01',
        enddate_str='today',
        bywhat='total' or 'day' or 'week' or 'month' or 'year'
    Returns:
        [label array<str>, pageviews array<int>]
    """
    response = get_social_report(analytics)
    return get_socialclicks(response)

def get_maxstep_report(analytics, startdate_str='2017-01-01', enddate_str='today'):
    """Queries the Analytics Reporting API V4.

    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        startdate_str, enddate_str: '2017-01-01', 'today', 'NdaysAgo'
    Returns:
        The Analytics Reporting API V4 response.
    """
    dimension_array = [{'name': 'ga:eventCategory'}, {'name': 'ga:eventAction'}]
    matric_array = [{'expression': 'ga:totalEvents'}]
    return analytics.reports().batchGet(
        body={
                'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': startdate_str, 'endDate': enddate_str}],
                    'metrics': matric_array,
                    'dimensions': dimension_array,
                    "includeEmptyRows": True
                }]
            }
    ).execute()

def get_maxsteps(response):
    """parse response, get the maxsteps # array

    Args:
        response: An Analytics Reporting API V4 response.
    Returns:
        [label array<str>, socialclicks array<int>]
    """
    max_array = []
    num_array = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])
            # print dimensions, dateRangeValues

            # generate one label
            max_str = ""
            for ele in dimensions:
                max_str = str(ele)
                if not max_str == 'maxstep':
                    max_array.append(max_str)
            # generate one pageviews
            num = 0
            for ele in dateRangeValues:
                num = int(ele[u'values'][0])
            num_array.append(num)
    print max_array, num_array

    dictionary = {}
    for i in range(len(max_array)):
        if max_array[i] != '[object Undefined]':
            dictionary[max_array[i]] = num_array[i]

    for i in range(0, 8):
        if str(i) not in dictionary:
            dictionary[str(i)] = 0
    print dictionary

    true_dictionary = {}

    for i in range(0, 7):
        true_dictionary[str(i)] = dictionary[str(i)] - dictionary[str(i + 1)]
    true_dictionary['7'] = dictionary['7']

    return true_dictionary

def get_maxstep_array(analytics):
    """get the pageviews # array

    Args:
        analytics: an initialized analytics object,
        startdate_str='2017-01-01',
        enddate_str='today',
        bywhat='total' or 'day' or 'week' or 'month' or 'year'
    Returns:
        [label array<str>, pageviews array<int>]
    """
    response = get_maxstep_report(analytics)
    dictionary = get_maxsteps(response)
    label = []
    stats = []
    for i in range(8):
        label.append(str(i))
        stats.append(dictionary[str(i)])
    return [label, stats]


def main():
    analytics = initialize_analyticsreporting()

    '''
    print get_pageviews_array(analytics, '6daysAgo', 'today', 'day')
    print get_pageviews_array(analytics, '27daysAgo', 'today', 'week')
    print get_pageviews_array(analytics, '2017-05-01', 'today', 'month')
    print get_pageviews_array(analytics, '2017-01-01', 'today', 'year')
    print get_pageviews_array(analytics, '2017-01-01', 'today', 'total')

    print get_socialclicks_array(analytics)
    '''

    print get_maxstep_array(analytics)


if __name__ == '__main__':
    main()
