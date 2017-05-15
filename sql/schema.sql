DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users(
    Uid bigserial PRIMARY KEY,
    Name TEXT,
    Email TEXT UNIQUE,
    Pass TEXT,
    Gender text check (Gender = 'Male' or Gender = 'Female'),
    Birthdate DATE,
    Ethnicity TEXT,
    Race TEXT
);
// YYYY-MM-DD
// Hispanic, Non-Hispanic
// Asian, Black, White, Other
DROP TABLE IF EXISTS Collisions CASCADE;
CREATE TABLE Collisions(
    Cid bigserial PRIMARY KEY,
    City TEXT,
    Street TEXT,
    CrossStreet TEXT,
    Cartype TEXT,
    PoliceFiled boolean,
    MedEvaluatedAtScene boolean,
    TakenToHosFromScene boolean,
    SeekedCareAfterward boolean,
    geom geometry NOT NULL,
    Uid int NOT NULL REFERENCES Users
);
// 'LINESTRING(0 0, 1 1, 2 1, 2 2)'
