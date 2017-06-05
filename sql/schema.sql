DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users(
    Uid int PRIMARY KEY,
    Name TEXT,
    Pass TEXT
);

DROP TABLE IF EXISTS Collisions CASCADE;
CREATE TABLE Collisions(
    Cid bigserial PRIMARY KEY,
    State TEXT,
    City TEXT,
    Street TEXT,
    CrossStreet TEXT,
    Cartype TEXT,
    PoliceFiled boolean,
    MedEvaluatedAtScene boolean,
    TakenToHosFromScene boolean,
    SeekedCareAfterward boolean,
    geom geometry NOT NULL,
    Gender text check (Gender = 'Male' or Gender = 'Female'),
    Age int,
    Ethnicity TEXT,
    Race TEXT,
    Uid int NOT NULL REFERENCES Users
);
// 'LINESTRING(0 0, 1 1, 2 1, 2 2)'
// Hispanic, Non-Hispanic
// Asian, Black, White, Other
