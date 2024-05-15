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

/*psql -d postgres -U postgres*/
/*psql -U postgres -d DataLab -a -f ./tableInitialize.sql*/
