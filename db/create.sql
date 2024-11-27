-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    balance FLOAT NOT NULL CHECK (balance >= 0)
);

CREATE TABLE Sellers (
    id INT NOT NULL PRIMARY KEY REFERENCES Users(id)
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(255),
    available BOOLEAN DEFAULT TRUE
);

CREATE TABLE CreatedProduct (
    pid INT NOT NULL REFERENCES Products(id),
    uid INT NOT NULL REFERENCES Users(id)
);

CREATE TABLE Tags (
    name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IsTagged (
    pid INT NOT NULL REFERENCES Products(id),
    name VARCHAR(255) NOT NULL REFERENCES Tags(name)
);

CREATE TABLE SoldBy (
    sid INT NOT NULL REFERENCES Sellers(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL,
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    UNIQUE (sid, pid)
);

CREATE TABLE Purchases (
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    sid INT NOT NULL REFERENCES Sellers(id),
    time_purchased TIMESTAMP WITHOUT TIME ZONE,
    quantity INT NOT NULL CHECK (quantity >= 0),
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    fulfilled BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (uid, pid, sid, time_purchased)
);

CREATE TABLE Reviews (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    description VARCHAR(255),
    time_created timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE ProductReviews (
    id INT NOT NULL REFERENCES Reviews(id),
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    PRIMARY KEY (uid, pid)
);

CREATE TABLE SellerReviews (
    id INT NOT NULL REFERENCES Reviews(id),
    uid INT NOT NULL REFERENCES Users(id),
    sid INT NOT NULL REFERENCES Sellers(id),
    PRIMARY KEY (uid, sid)
);

CREATE TABLE Categories (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE CategoryOf (
    pid INT NOT NULL REFERENCES Products(id),
    cid INT NOT NULL REFERENCES Categories(id),
    PRIMARY KEY(pid)
);

CREATE TABLE Inventory (
    sid INT NOT NULL REFERENCES Sellers(id),
    pid INT NOT NULL REFERENCES Products(id),
    quantity INT NOT NULL,
    UNIQUE (sid, pid)
);

CREATE TABLE Helpfulness (
    rid INT NOT NULL REFERENCES Reviews(id),
    uid INT NOT NULL REFERENCES Users(id),
    value INT CHECK (value IN (-1, 0, 1)),
    PRIMARY KEY (uid, rid)
);