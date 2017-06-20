DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users(
    Uid int PRIMARY KEY,
    Name TEXT,
    Pass TEXT
);

INSERT INTO Users(uid, name, pass)
VALUES (1, 'admin', 'ipim_admin');

uid | name  |   pass
-----+-------+-----------
  1 | admin | ipim_admin

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
    Analyzed boolean default 'false'
);
// 'LINESTRING(0 0, 1 1, 2 1, 2 2)'
// Hispanic, Non-Hispanic
// Asian, Black, White, Other

// psql postgres
