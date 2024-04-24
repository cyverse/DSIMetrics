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
    FOREIGN KEY (ZoomMeetingID) REFERENCES ZoomRefreshTokens(ZoomMeetingID)
);

CREATE TABLE Workshops (
    WorkshopID SERIAL PRIMARY KEY,
    SeriesID INTEGER NOT NULL,
    WorkshopName VARCHAR(255) NOT NULL,
    WorkshopDate DATE NOT NULL,
    FOREIGN KEY (SeriesID) REFERENCES Series(SeriesID) 
);

CREATE TABLE RegistreeWorkshops (
    RegID BIGINT NOT NULL,
    WorkshopID INTEGER NOT NULL,
    Registered BOOLEAN,
    CheckedIn Boolean,
    PRIMARY KEY (RegID, WorkshopID),
    FOREIGN KEY (RegID) REFERENCES RegistreeInfo(RegID),
    FOREIGN KEY (WorkshopID) REFERENCES Workshops(WorkshopID)
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
    FOREIGN KEY (WorkshopID) REFERENCES Workshops(WorkshopID)
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

/*Select attendance over time based on series and semester*/
-- SELECT WeekStarting, SUM(TotalCount) AS TotalCount
-- FROM (
--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, COUNT(RegistreeWorkshops.RegID) as TotalCount 
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester}} AND RegistreeWorkshops.CheckedIn = TRUE
--     GROUP BY WeekStarting

--     UNION ALL

--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, COUNT(UnknownPeople.FirstName) as TotalCount 
--     FROM UnknownPeople
--     LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester}}
--     GROUP BY WeekStarting
-- ) AS combined_data
-- GROUP BY WeekStarting
-- ORDER BY WeekStarting;

-- /*Total Attendance*/
-- SELECT
-- (SELECT COUNT(RegistreeWorkshops.RegID) as TotalCount 
-- FROM RegistreeWorkshops
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester}} AND RegistreeWorkshops.CheckedIn = TRUE)
-- +
-- (SELECT COUNT(UnknownPeople.FirstName) as TotalCount 
-- FROM UnknownPeople
--     LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester}})
-- AS TotalCount;



-- /*Select attendance over time for one series*/
-- SELECT WeekStarting, SUM(TotalCount) AS TotalCount
-- FROM (
--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, COUNT(RegistreeWorkshops.RegID) as TotalCount 
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesID = {{ seriesID }} AND RegistreeWorkshops.CheckedIn = TRUE
--     GROUP BY WeekStarting

--     UNION ALL

--     SELECT DATE_TRUNC('week', Workshops.WorkshopDate)::DATE AS WeekStarting, COUNT(UnknownPeople.FirstName) as TotalCount 
--     FROM UnknownPeople
--     LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesID = {{ seriesID }}
--     GROUP BY WeekStarting
-- ) AS combined_data
-- GROUP BY WeekStarting
-- ORDER BY WeekStarting;

-- /*Total Attendance based on series*/
-- SELECT
-- (SELECT COUNT(RegistreeWorkshops.RegID) as TotalCount 
-- FROM RegistreeWorkshops
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesID = {{ seriesID }} AND RegistreeWorkshops.CheckedIn = TRUE)
-- +
-- (SELECT COUNT(UnknownPeople.FirstName) as TotalCount 
-- FROM UnknownPeople
-- LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesID = {{ seriesID }})
-- AS TotalCount;
;

/*Total Attendance*/
-- SELECT 
--     CheckedIn.CheckedIn,
--     Attended.Attended,
--     CheckedIn.CheckedIn + Attended.Attended AS TotalPeopleAttended
-- FROM
--     (SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as CheckedIn
--      FROM RegistreeWorkshops
--      LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--      LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--      WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.CheckedIn = TRUE) AS CheckedIn,
     
--     (SELECT COUNT(DISTINCT CONCAT(UnknownPeople.FirstName, UnknownPeople.LastName)) as Attended
--      FROM UnknownPeople
--      LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
--      LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--      WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP') AS Attended;

-- /*All registered participants*/
-- SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as Registered
-- FROM RegistreeWorkshops 
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = True;

-- /*People who checked in and registered for at least one workshop*/
-- SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as CheckedReg
-- FROM RegistreeWorkshops
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = True AND RegistreeWorkshops.CheckedIn = True;

-- /*People who checked in for a workshop but didnt register (maybe add unknownpeople)*/
-- SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as CheckedNoReg
-- FROM RegistreeWorkshops
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = FALSE AND RegistreeWorkshops.CheckedIn = True;

-- /*Gets All people who registered for a workshop and didnt attend a single one*/
-- SELECT COUNT(DISTINCT RegID) as RegNoChecked
-- FROM RegistreeWorkshops
-- LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
-- LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
-- WHERE Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = TRUE 
-- AND RegistreeWorkshops.RegID NOT IN (
--     SELECT DISTINCT RegID
--     FROM RegistreeWorkshops
--     WHERE CheckedIn = TRUE
-- );

-- /*One combined query*/
-- WITH TotalAttendance AS (
--     SELECT 
--         COUNT(DISTINCT CASE WHEN rw.CheckedIn = TRUE THEN rw.RegID END) AS CheckedIn,
--         COUNT(DISTINCT CASE WHEN up.FirstName IS NOT NULL THEN CONCAT(up.FirstName, up.LastName) END) AS Attended
--     FROM RegistreeWorkshops rw
--     LEFT JOIN Workshops w ON w.WorkshopID = rw.WorkshopID
--     LEFT JOIN Series s ON s.SeriesID = w.SeriesID
--     LEFT JOIN UnknownPeople up ON w.WorkshopID = up.WorkshopID
--     WHERE s.SeriesYear = '2024' AND s.Semester = 'SP'
-- ),
-- AllRegistered AS (
--     SELECT COUNT(DISTINCT RegID) as Registered
--     FROM RegistreeWorkshops 
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.Registered = TRUE
-- ),
-- CheckedRegistered AS (
--     SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as CheckedReg
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.Registered = TRUE AND RegistreeWorkshops.CheckedIn = TRUE
-- ),
-- CheckedNoRegistered AS (
--     SELECT COUNT(DISTINCT RegistreeWorkshops.RegID) as CheckedNoReg
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.Registered = FALSE AND RegistreeWorkshops.CheckedIn = TRUE
-- ),
-- RegisteredNoChecked AS (
--     SELECT COUNT(DISTINCT RegID) as RegNoChecked
--     FROM RegistreeWorkshops
--     LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--     LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.Registered = TRUE 
--     AND RegistreeWorkshops.RegID NOT IN (
--         SELECT DISTINCT RegID
--         FROM RegistreeWorkshops
--         WHERE CheckedIn = TRUE
--     )
-- )
-- SELECT 
--     ta.CheckedIn,
--     ta.Attended,
--     ta.CheckedIn + ta.Attended AS TotalPeopleAttended,
--     ar.Registered,
--     cr.CheckedReg,
--     cnr.CheckedNoReg,
--     rnc.RegNoChecked
-- FROM 
--     TotalAttendance ta,
--     AllRegistered ar,
--     CheckedRegistered cr,
--     CheckedNoRegistered cnr,
--     RegisteredNoChecked rnc;


-- /*Same query just transposed*/
-- WITH TotalAttendance AS (
--     SELECT 
--         COUNT(DISTINCT CASE WHEN rw.CheckedIn = TRUE THEN rw.RegID END) AS CheckedIn,
--         COUNT(DISTINCT CASE WHEN up.FirstName IS NOT NULL THEN CONCAT(up.FirstName, up.LastName) END) AS Attended
--     FROM 
--         RegistreeWorkshops rw
--         LEFT JOIN Workshops w ON w.WorkshopID = rw.WorkshopID
--         LEFT JOIN Series s ON s.SeriesID = w.SeriesID
--         LEFT JOIN UnknownPeople up ON w.WorkshopID = up.WorkshopID
--     WHERE 
--         s.SeriesYear = {{ seriesYear }} AND s.Semester = {{ semester }}
-- ),
-- AllRegistered AS (
--     SELECT COUNT(DISTINCT RegID) as Registered
--     FROM 
--         RegistreeWorkshops 
--         LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--         LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE 
--         Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = TRUE
-- ),
-- CheckedRegistered AS (
--     SELECT COUNT(DISTINCT RegID) as CheckedReg
--     FROM 
--         RegistreeWorkshops
--         LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--         LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE 
--         Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = TRUE AND RegistreeWorkshops.CheckedIn = TRUE
-- ),
-- CheckedNoRegistered AS (
--     SELECT COUNT(DISTINCT RegID) as CheckedNoReg
--     FROM 
--         RegistreeWorkshops
--         LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--         LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE 
--         Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = FALSE AND RegistreeWorkshops.CheckedIn = TRUE
-- ),
-- RegisteredNoChecked AS (
--     SELECT COUNT(DISTINCT RegID) as RegNoChecked
--     FROM 
--         RegistreeWorkshops
--         LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
--         LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
--     WHERE 
--         Series.SeriesYear = {{ seriesYear }} AND Series.Semester = {{ semester }} AND RegistreeWorkshops.Registered = TRUE 
--         AND RegistreeWorkshops.RegID NOT IN (
--             SELECT DISTINCT RegID
--             FROM RegistreeWorkshops
--             WHERE CheckedIn = TRUE
--         )
-- )
-- SELECT 
--     'Registered' AS Metric, 
--     Registered AS Value 
-- FROM 
--     AllRegistered
-- UNION ALL
-- SELECT 
--     'TotalAttended' AS Metric, 
--     CheckedIn + Attended AS Value 
-- FROM 
--     TotalAttendance
-- UNION ALL
-- SELECT 
--     'CheckedIn' AS Metric, 
--     CheckedIn AS Value 
-- FROM 
--     TotalAttendance
-- UNION ALL
-- SELECT 
--     'Attended' AS Metric, 
--     Attended AS Value 
-- FROM 
--     TotalAttendance
-- UNION ALL
-- SELECT 
--     'CheckReg' AS Metric, 
--     CheckedReg AS Value 
-- FROM 
--     CheckedRegistered
-- UNION ALL
-- SELECT 
--     'CheckNoReg' AS Metric, 
--     CheckedNoReg AS Value 
-- FROM 
--     CheckedNoRegistered
-- UNION ALL
-- SELECT 
--     'RegNoChecked' AS Metric, 
--     RegNoChecked AS Value 
-- FROM 
--     RegisteredNoChecked;


