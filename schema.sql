DROP TABLE IF EXISTS slots;

CREATE TABLE slots
(
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    time Integer NOT NULL,
    time_length Text NOT NULL,
    gym TEXT NOT NULL,
    trainer TEXT NOT NULL,
    date CURRENT_DATE
);

INSERT INTO slots (time,gym,time_length, trainer, date)
VALUES
    ("10","first floor", "1.5hrs", "Josh",CURRENT_DATE),
    ("10","second floor", "1.5hrs","Ethan",CURRENT_DATE),
    ("13","first floor", "1.5hrs", "Odhran",CURRENT_DATE),
    ("13","second floor", "1.5hrs", "Josh",CURRENT_DATE),
    ("16","first floor", "1.5hrs", "Simon",CURRENT_DATE),
    ("16","second floor", "1.5hrs", "Odhran",CURRENT_DATE),
    ("18.5","first floor", "1.5hrs", "Ethan",CURRENT_DATE),
    ("18.5","second floor", "1.5hrs", "Josh",CURRENT_DATE),
    ("20","first floor", "1.5hrs", "Odhran",CURRENT_DATE)
;

SELECT *
from slots 

DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id Text NOT NULL,
    password Text NOT NULL
);

SELECT * 
from users

DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings
(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id integer not null,
    user_id text NOT NULL,
    time Integer NOT NULL,
    gym TEXT NOT NULL,
    trainer TEXT NOT NULL,
    date date not null
);

select *
from bookings

DROP TABLE IF EXISTS history;


SELECT *
from history

CREATE TABLE card
(
    card_id Integer PRIMARY KEY AUTOINCREMENT,
    user_id integer not null,
    amount integer not null
);
select *
from card

CREATE Table card_points
(
    card_id Integer PRIMARY KEY AUTOINCREMENT,
    user_id integer not null,
    points integer not null
);

SELECT *
from card_points
