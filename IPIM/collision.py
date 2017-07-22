import datetime
import time
from sqlalchemy.orm import sessionmaker

class Collision(object):
    cid = long(-1)

    acc_date = None

    state = ""
    city = ""
    street = ""
    cross_street = ""

    cartype = ""
    time_of_day = ""
    police_filed = False
    med_evaluated_at_scene = False
    taken_to_hos_from_scene = False
    seeked_care_afterward = False

    geom = ""

    gender = ""
    age = 0
    ethnicity = ""
    race = ""

    timespent = 0
    referURL = ''

    def __init__(self, form):

        self.gender = ""
        self.age = 0
        self.ethnicity = ""
        self.race = ""

        # parse date
        acc_date_str_ms = form['answer_date'] # in string of milliseconds since midnight Jan 1 1970
        time_ts = time.gmtime(long(acc_date_str_ms)/1000.0)
        self.acc_date = datetime.datetime.fromtimestamp(time.mktime(time_ts))

        # parse "state, city, street, cross_street"
        state_city_st_cst = form['answer_state_city_st_cst']
        if len(state_city_st_cst) !=0 :
            state_city_st_cst_list = state_city_st_cst.split(", ")
            self.state = state_city_st_cst_list[0].strip()
            self.city = state_city_st_cst_list[1].strip()
            self.street = state_city_st_cst_list[2].strip()
            self.cross_street = state_city_st_cst_list[3].strip()

        # parse answer 1 ~ 6 :
        answer_list = []
        for i in range(1, 7):
            answer_list.append(form['answer' + str(i)])

        self.cartype = answer_list[0]
        self.time_of_day = answer_list[1]
        self.police_filed = True if (answer_list[2] == "Yes") else False
        self.med_evaluated_at_scene = True if (answer_list[3] == "Yes") else False
        self.taken_to_hos_from_scene = True if (answer_list[4] == "Yes") else False
        self.seeked_care_afterward = True if (answer_list[5] == "Yes") else False

        # parse geom
        geo_list_str = form['answer_route']
        geo_list_strs = geo_list_str.split(",")
        geo_str = ""
        for i in range(0, len(geo_list_strs)/2):
            geo_str += geo_list_strs[i * 2]
            geo_str += " "
            geo_str += geo_list_strs[i * 2 + 1]
            if i != (len(geo_list_strs)/2 - 1):
                geo_str += ","
        self.geom = 'LINESTRING(' + geo_str + ')'

        # parse user info
        self.gender = form['answer_gender']
        self.age = form['answer_age']
        self.ethnicity = form['answer_ethnicity']
        self.race = form['answer_race']

        self.timespent = form['timespent']
        self.referURL = form['referURL']

        # self.printCollisionInfo()

    # insert into collisions table
    def syncToDBWithUid(self, some_engine):

        DB_Session = sessionmaker(bind=some_engine)
        db_session = DB_Session()

        try:
            db_session.execute('''
                INSERT INTO Collisions (
                AccDate, State, City, Street, CrossStreet,
                Cartype, TimeOfDay,
                PoliceFiled, MedEvaluatedAtScene, TakenToHosFromScene, SeekedCareAfterward,
                geom,
                Gender, Age, Ethnicity, Race,
                TimeSpent, ReferURL )
                VALUES (
                :acc_date, :state, :city, :street, :cross,
                :cartype, :time_of_day,
                :police, :med, :taken, :seek,
                :geom,
                :gender, :age, :enth, :race,
                :TimeSpent, :ReferURL )
                ''', {
                "acc_date":self.acc_date,"state":self.state,"city":self.city, "street":self.street, "cross":self.cross_street,
                "cartype":self.cartype, "time_of_day": self.time_of_day,
                "police":str(self.police_filed), "med":str(self.med_evaluated_at_scene),
                "taken":str(self.taken_to_hos_from_scene), "seek":str(self.seeked_care_afterward),
                "geom":self.geom,
                "gender":self.gender, "age":self.age, "enth":self.ethnicity, "race":self.race,
                "TimeSpent":self.timespent, "ReferURL":self.referURL
                }
            )
            cur = db_session.execute('''
                SELECT count(*)
                FROM Collisions
                '''
            )
            db_session.commit()
            new_cid = cur.fetchone()
            # print "new cid is ", str(new_cid[0])
            self.cid = new_cid;
        except:
            db_session.rollback()
            raise

    def printCollisionInfo(self):
        # check if all passed in are correct
        print "a new collision instance"
        print "cartype", self.cartype
        print "state", self.state
        print "city", self.city
        print "street", self.street
        print "time_of_day", self.time_of_day
        print "cross_street", self.cross_street
        print "police_filed", self.police_filed
        print "med_evaluated_at_scene", self.med_evaluated_at_scene
        print "taken_to_hos_from_scene", self.taken_to_hos_from_scene
        print "seeked_care_afterward", self.seeked_care_afterward
        print "acc_date", self.acc_date
        print "geom", self.geom
        print "gender", self.gender
        print "age", self.age
        print "ethn", self.ethnicity
        print "race", self.race
