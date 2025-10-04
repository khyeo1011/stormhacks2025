CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL,
    Nickname VARCHAR(256),
    cumulativeScore INT
);

CREATE TABLE Prediction (
    predictionID SERIAL PRIMARY KEY,
    tripID INT,
    userID SERIAL,
    late BOOLEAN,
    FOREIGN KEY (userID) REFERENCES Users(id)
);

CREATE TABLE Friends (
    userID1 INT,
    userID2 INT,
    PRIMARY KEY (userID1, userID2),
    FOREIGN KEY (userID1) REFERENCES Users(id),
    FOREIGN KEY (userID2) REFERENCES Users(id),
    CHECK (userID1 <> userID2)
);