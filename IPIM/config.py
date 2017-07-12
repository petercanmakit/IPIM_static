# this config file is for the whole project, not for flask

'''
Configuration for database
'''
db_config_develop = {
	'host': '127.0.0.1',
    'user': 'peter',
    'passwd': '940611',
    'db': 'geo',
    'dbtype': 'postgresql'
}

db_config_deploy = {
	'host': '127.0.0.1',
    'user': 'peter',
    'passwd': '940611',
    'db': 'ipim',
    'dbtype': 'postgresql'
}

# db_config = db_config_develop
db_config = db_config_deploy

DATABASE_URI = db_config['dbtype'] + '://' + db_config['user'] + ':' + db_config['passwd'] + '@' + db_config['host'] + '/' + db_config['db']
# DATABASE_URI = "postgresql://peter:940611@127.0.0.1/geo" # mac
# DATABASE_URI = "postgresql://ipim:admin_ipim@127.0.0.1/ipim" # gg cloud linux vm

'''
Configuration for Google Analytics Reporting V4
'''
ga_config = {
    'SCOPES': ['https://www.googleapis.com/auth/analytics.readonly'],
    'KEY_FILE_LOCATION': 'docs/ga/IPIM-742550970c79.json',
    'VIEW_ID': '153403983'
}

'''
Configuration for ssl key and credential
'''
ssl_config = {
    'CRT_PATH': 'docs/ssl/ipim.crt',
    'KEY_PATH': 'docs/ssl/ipim.key'
}
