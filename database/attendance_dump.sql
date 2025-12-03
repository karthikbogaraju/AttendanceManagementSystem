BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "attendance" (
	"id"	INTEGER,
	"student_id"	INTEGER NOT NULL,
	"course_id"	INTEGER NOT NULL,
	"date"	TEXT NOT NULL,
	"status"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("course_id") REFERENCES "courses"("id"),
	FOREIGN KEY("student_id") REFERENCES "students"("id")
);
CREATE TABLE IF NOT EXISTS "courses" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "student_courses" (
	"id"	INTEGER,
	"student_id"	INTEGER NOT NULL,
	"course_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("student_id","course_id"),
	FOREIGN KEY("course_id") REFERENCES "courses"("id"),
	FOREIGN KEY("student_id") REFERENCES "students"("id")
);
CREATE TABLE IF NOT EXISTS "students" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"email"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "teacher_courses" (
	"id"	INTEGER,
	"teacher_id"	INTEGER NOT NULL,
	"course_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	UNIQUE("teacher_id","course_id"),
	FOREIGN KEY("course_id") REFERENCES "courses"("id"),
	FOREIGN KEY("teacher_id") REFERENCES "teachers"("id")
);
CREATE TABLE IF NOT EXISTS "teachers" (
	"id"	INTEGER,
	"name"	TEXT NOT NULL,
	"email"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "attendance" VALUES (1,1,1,'2025-12-02','Present');
INSERT INTO "attendance" VALUES (2,2,1,'2025-12-02','Absent');
INSERT INTO "courses" VALUES (1,'Python 101');
INSERT INTO "courses" VALUES (2,'Data Structures');
INSERT INTO "courses" VALUES (3,'Java');
INSERT INTO "courses" VALUES (4,'AI Basics');
INSERT INTO "student_courses" VALUES (1,1,1);
INSERT INTO "student_courses" VALUES (2,2,1);
INSERT INTO "student_courses" VALUES (3,3,2);
INSERT INTO "student_courses" VALUES (4,4,2);
INSERT INTO "student_courses" VALUES (5,4,3);
INSERT INTO "student_courses" VALUES (6,6,1);
INSERT INTO "student_courses" VALUES (7,6,3);
INSERT INTO "student_courses" VALUES (8,7,4);
INSERT INTO "student_courses" VALUES (9,8,2);
INSERT INTO "student_courses" VALUES (10,8,4);
INSERT INTO "students" VALUES (1,'Student One','student1@example.com','studpass1');
INSERT INTO "students" VALUES (2,'mike','mike@example.com','password');
INSERT INTO "students" VALUES (3,'paul','paul@example.com','password');
INSERT INTO "students" VALUES (4,'bhanu','bhanu@example.com','password');
INSERT INTO "students" VALUES (5,'pavitra','pavitra@example.com','password');
INSERT INTO "students" VALUES (6,'anirudh','anirudh@example.com','password');
INSERT INTO "students" VALUES (7,'steven','steven@example.com','password');
INSERT INTO "students" VALUES (8,'mary','mary@example.com','password');
INSERT INTO "teacher_courses" VALUES (1,1,1);
INSERT INTO "teacher_courses" VALUES (2,1,2);
INSERT INTO "teacher_courses" VALUES (3,1,3);
INSERT INTO "teacher_courses" VALUES (4,2,2);
INSERT INTO "teacher_courses" VALUES (5,2,4);
INSERT INTO "teachers" VALUES (1,'Test Teacher','teacher@example.com','password123');
INSERT INTO "teachers" VALUES (2,'teacher1','teacher1@example.com','password123');
COMMIT;
