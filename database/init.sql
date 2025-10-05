-- Users Table
CREATE TABLE "users" (
    "id" SERIAL PRIMARY KEY,
    "email" VARCHAR(255) UNIQUE NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "nickname" VARCHAR(50),
    "cumulativeScore" INT DEFAULT 0,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Friends Table: Using a self-referencing many-to-many relationship
CREATE TABLE "friends" (
    "userId" INT NOT NULL,
    "friendId" INT NOT NULL,
    PRIMARY KEY ("userId", "friendId"),
    FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY ("friendId") REFERENCES "users"("id") ON DELETE CASCADE,
    CHECK ("userId" <> "friendId") -- Ensures a user cannot be friends with themselves
);

-- Friend Requests Table
CREATE TABLE "friendRequests" (
    "id" SERIAL PRIMARY KEY,
    "senderId" INT NOT NULL,
    "receiverId" INT NOT NULL,
    "status" VARCHAR(20) DEFAULT 'pending', -- e.g., 'pending', 'accepted', 'rejected'
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("senderId") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY ("receiverId") REFERENCES "users"("id") ON DELETE CASCADE,
    CHECK ("senderId" <> "receiverId") -- User cannot send a request to themselves
);

-- Trips Table
CREATE TABLE "trips" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "route_id" INT,
    "headsign" VARCHAR(255),
    "description" TEXT,
    "outcome" VARCHAR(255),
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Predictions Table
CREATE TABLE "predictions" (
    "id" SERIAL PRIMARY KEY,
    "userId" INT NOT NULL,
    "tripId" INT NOT NULL,
    "predictedOutcome" VARCHAR(255) NOT NULL,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY ("tripId") REFERENCES "trips"("id") ON DELETE CASCADE
);
