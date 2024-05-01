DROP TABLE RegistreeInfo CASCADE;
DROP TABLE Series CASCADE;
DROP TABLE Workshops CASCADE;
DROP TABLE RegistreeWorkshops CASCADE;
DROP TABLE ProgramVariables CASCADE;
DROP TABLE ZoomRefreshTokens CASCADE;
DROP TABLE UnknownPeople CASCADE;

CREATE TABLE RegistreeInfo (
    RegID BIGINT PRIMARY KEY,
    FirstName VARCHAR(30),
    LastName VARCHAR(30),
    NetID VARCHAR(30),
    Email VARCHAR(50),
    College VARCHAR(255),
    Department VARCHAR(255),
    Major VARCHAR(255),
    Recontact BOOLEAN
);

CREATE TABLE ZoomRefreshTokens (
    ZoomMeetingID TEXT PRIMARY KEY,
    RefreshToken TEXT
);

CREATE TABLE Series (
    SeriesID SERIAL PRIMARY KEY,
    SeriesName VARCHAR(255) NOT NULL,
    ZoomMeetingID TEXT NOT NULL,
    QualtricsID Text NOT NULL,
    SeriesURL TEXT NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Semester VARCHAR (2) NOT NULL,
    SeriesYear VARCHAR(4) NOT NULL,
    FOREIGN KEY (ZoomMeetingID) REFERENCES ZoomRefreshTokens(ZoomMeetingID) ON DELETE CASCADE
);

CREATE TABLE Workshops (
    WorkshopID SERIAL PRIMARY KEY,
    SeriesID INTEGER NOT NULL,
    WorkshopName VARCHAR(255) NOT NULL,
    WorkshopDate DATE NOT NULL,
    FOREIGN KEY (SeriesID) REFERENCES Series(SeriesID) ON DELETE CASCADE
);

CREATE TABLE RegistreeWorkshops (
    RegID BIGINT NOT NULL,
    WorkshopID INTEGER NOT NULL,
    Registered BOOLEAN,
    CheckedIn Boolean,
    PRIMARY KEY (RegID, WorkshopID),
    FOREIGN KEY (RegID) REFERENCES RegistreeInfo(RegID) ON DELETE CASCADE,
    FOREIGN KEY (WorkshopID) REFERENCES Workshops(WorkshopID) ON DELETE CASCADE
);

CREATE TABLE ProgramVariables (
    ElementName VARCHAR(255) PRIMARY KEY,
    ElementValue TEXT NOT NULL
);

CREATE TABLE UnknownPeople (
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    WorkshopID INTEGER,
    PRIMARY KEY (FirstName, LastName, WorkshopID),
    FOREIGN KEY (WorkshopID) REFERENCES Workshops(WorkshopID) ON DELETE CASCADE
);

INSERT INTO ZoomRefreshTokens
VALUES
('86423223879', 'eyJzdiI6IjAwMDAwMSIsImFsZyI6IkhTNTEyIiwidiI6IjIuMCIsImtpZCI6IjFjNDlkYTQzLTExNDctNDkyOC1hZmViLWFiZWNjMmZjMGNiOCJ9.eyJ2ZXIiOjksImF1aWQiOiJlNzc0NWYwZTI0NTg4Y2Q2MTY4NGEzYTg3ZDc5MTk5OCIsImNvZGUiOiJMbkNhOU9TcFQ0eVZXTF9qX2dFVHRpcHJoQVgxVHlIX0EiLCJpc3MiOiJ6bTpjaWQ6UWhoWmZIYXdSbE4xdEtqNkJ2S1BBIiwiZ25vIjowLCJ0eXBlIjoxLCJ0aWQiOjUsImF1ZCI6Imh0dHBzOi8vb2F1dGguem9vbS51cyIsInVpZCI6InNNeUFjYWF4VFJxSXhMMXBtcU9fdHciLCJuYmYiOjE3MTE5OTk0NTksImV4cCI6MTcxOTc3NTQ1OSwiaWF0IjoxNzExOTk5NDU5LCJhaWQiOiJyakZvWFF5R1RuR2tyNnJXdVhaZWJ3In0.9nNjoLFaeqMdqwUX_aeHbQDaX_aV74W3k02ZdAietvrLLoXURe18wZrfv1nivdzL5gekOCd4-O9ceHRgv4jqvQ');

INSERT INTO ProgramVariables
VALUES 
('check_in_form_id', '1bxU3Oydiv6sUjMsDCHWjHsEqkNz6Do1O-8b8mGymJa8'),
('qualtrics_api_token', 'egl9Nc1pKnEswZ1hUMfXjjNJ50wTP9LhBHcJa4XF'),
('zoom_client_id', 'QhhZfHawRlN1tKj6BvKPA'),
('zoom_client_secret', '6Wzb66E3my9VPAS8CQ262QKHplsPk37v');

/*psql -d postgres -U postgres*/
/*psql -U postgres -d DataLab -a -f ./tableInitialize.sql*/


-- SELECT WeekStarting, WorkshopName, SUM(TotalCount) AS TotalCount
-- FROM (
--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, Workshops.WorkshopName, COUNT(RegistreeWorkshops.RegID) as TotalCount 
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesID = 1 AND RegistreeWorkshops.CheckedIn = TRUE
--     GROUP BY WeekStarting, Workshops.WorkshopName

--     UNION ALL

--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, Workshops.WorkshopName, COUNT(UnknownPeople.FirstName) as TotalCount 
--     FROM UnknownPeople
--     LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesID = 1
--     GROUP BY WeekStarting, Workshops.WorkshopName
-- ) AS combined_data
-- GROUP BY WeekStarting, WorkshopName
-- ORDER BY WeekStarting;
