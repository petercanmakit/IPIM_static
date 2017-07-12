import datetime
import time
import radar
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

import IPIM.config as cfg

def createSchema(some_engine):
	DB_Session = sessionmaker(bind=some_engine)
	db_session = DB_Session()

	try:
		db_session.execute('''
			DROP TABLE IF EXISTS Users CASCADE;
			CREATE TABLE Users(
				Uid int PRIMARY KEY,
				Name TEXT,
				Pass TEXT
			);

			INSERT INTO Users(uid, name, pass)
			VALUES (1, 'admin', 'ipim_admin');

			DROP TABLE IF EXISTS Collisions CASCADE;
			CREATE TABLE Collisions(
				Cid bigserial PRIMARY KEY,
				AccDate Date,
				State TEXT,
				City TEXT,
				Street TEXT,
				CrossStreet TEXT,
				Cartype TEXT,
				TimeOfDay TEXT,
				PoliceFiled boolean,
				MedEvaluatedAtScene boolean,
				TakenToHosFromScene boolean,
				SeekedCareAfterward boolean,
				geom geometry NOT NULL,
				Gender text check (Gender = 'Male' or Gender = 'Female' or Gender = 'not_answered'),
				Age int,
				Ethnicity TEXT,
				Race TEXT,
				SubmitType TEXT default 'user',
				SubmittedDate Date default CURRENT_DATE
			);
			'''
		)
		db_session.commit()
		print "schema created on success!"
	except:
		db_session.rollback()
		raise

def generateRandomDate(startstr, stopstr):
	'''
	start='2000-05-24', stop='2013-05-24T23:59:59'
	start = datetime.datetime(year=2000, month=5, day=24),
    stop = datetime.datetime(year=2013, month=5, day=24)
    "now" -> datetime.datetime.now()
    return a date string
	'''
	startdate = startstr
	if stopstr == 'now':
		stopdate = datetime.datetime.now()
	else:
		stopdate = stopstr
	return radar.random_datetime(
    			start = startdate,
    			stop = stopdate
			).isoformat()

def insertTestData(some_engine, some_accdate, some_submitdate):
	DB_Session = sessionmaker(bind=some_engine)
	db_session = DB_Session()

	try:
		db_session.execute('''
			INSERT INTO Collisions (
			AccDate,
			geom,
			Gender,
			SubmitType,
    		SubmittedDate )
			VALUES (
			:acc_date,
			:geom,
			:gender,
			:submittype,
			:submitteddate )
			''', {
			"acc_date": some_accdate,
			"geom": 'LINESTRING(0 0, 1 1)',
			"gender": 'not_answered',
			"submittype": 'test',
			"submitteddate": some_submitdate
			}
		)
		db_session.commit()
	except:
		db_session.rollback()
		raise


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--create', is_flag=True)
	@click.option('--insert', is_flag=True)
	@click.argument('SETS', default=100, type=int)
	# @click.argument('PORT', default=8111, type=int)
	def run(create, insert, sets):
		"""
		--create for create table schema\n
		--insert for inserting test sets\n
		SETS for number fo test datasets of insersion
		"""
		SETS = sets
		DATABASEURI = cfg.DATABASE_URI
		engine = create_engine(DATABASEURI)
		if create :
			createSchema(engine)
		elif insert :
			for i in range(SETS):
				acc_date = generateRandomDate("2017-04-01", 'now')
				sub_date = generateRandomDate(acc_date , 'now')
				# print sub_date
				insertTestData(engine, acc_date, sub_date)
			print str(SETS) + " test datasets inserted on success"
		else:
			print "arguments wrong..."

	run()
