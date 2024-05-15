
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

SELECT combined_data.SeriesName, SUM(combined_data.TotalCount) AS TotalCount, SUM(combined_data.UniqueTotal) AS UniqueTotal
FROM (
    SELECT series.SeriesName, COUNT(RegistreeWorkshops.RegID) as TotalCount, COUNT(DISTINCT RegistreeWorkshops.RegID) as UniqueTotal
    FROM RegistreeWorkshops
    LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
    LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
    WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP' AND RegistreeWorkshops.CheckedIn = TRUE
    GROUP BY Series.SeriesName

    UNION ALL

    SELECT Series.SeriesName, COUNT(UnknownPeople.FirstName) as TotalCount, COUNT(DISTINCT CONCAT(UnknownPeople.FirstName, UnknownPeople.LastName)) as UniqueTotal
    FROM UnknownPeople
    LEFT JOIN Workshops ON Workshops.WorkshopID = UnknownPeople.WorkshopID
    LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
    WHERE Series.SeriesYear = '2024' AND Series.Semester = 'SP'
    GROUP BY Series.SeriesName
) AS combined_data
GROUP BY combined_data.SeriesName
ORDER BY combined_data.SeriesName;


SELECT * FROM RegistreeWorkshops
LEFT JOIN Workshops ON Workshops.WorkshopID = RegistreeWorkshops.WorkshopID
LEFT JOIN Series ON Series.SeriesID = Workshops.SeriesID
WHERE Series.SeriesID = 5;

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