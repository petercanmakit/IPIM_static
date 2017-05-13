DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users(
    Uid bigserial PRIMARY KEY,
    Name TEXT,
    Email TEXT,
    Pass TEXT,
    Gender char(7) check (Gender = 'male' or Gender = 'female'),
    Birthdate DATE, // YYYY-MM-DD
    Ethnicity char(13), // Hispanic, Non-Hispanic
    Race char(6) // Asian, Black, White, Other
);

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
    geom geometry NOT NULL, // 'LINESTRING(0 0, 1 1, 2 1, 2 2)'
    Uid int NOT NULL REFERENCES Users
);
