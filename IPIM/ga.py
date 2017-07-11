"""A wapper for Analytics Reporting API V4."""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'IPIM-742550970c79.json'
VIEW_ID = '153403983'


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

def main():
	analytics = initialize_analyticsreporting()

	print get_pageviews_array(analytics, '6daysAgo', 'today', 'day')
	print get_pageviews_array(analytics, '27daysAgo', 'today', 'week')
	print get_pageviews_array(analytics, '2017-05-01', 'today', 'month')
	print get_pageviews_array(analytics, '2017-01-01', 'today', 'year')
	print get_pageviews_array(analytics, '2017-01-01', 'today', 'total')

if __name__ == '__main__':
	main()
