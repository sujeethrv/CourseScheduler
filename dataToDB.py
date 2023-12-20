import pandas as pd
import mysql.connector
from sqlalchemy import create_engine


host = 'localhost'
database = 'courseSchedulerDB'
user = 'root'
password = 'Useme123'

conn = mysql.connector.connect(host=host, user=user, password=password)
cursor = conn.cursor()
cursor.execute("DROP DATABASE courseschedulerdb")
try:
    cursor.execute("DELETE DATABASE courseschedulerdb")
except:
    pass
cursor.execute("CREATE DATABASE IF NOT EXISTS courseschedulerdb")
conn.commit()

conn.close()

conn = mysql.connector.connect(host=host, database='courseschedulerdb', user=user, password=password)
cursor = conn.cursor()

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

excel_path = "./CourseSchedulerData.xlsx"
xl = pd.ExcelFile(excel_path)

create_table_commands = {

    "Department":
        '''
        CREATE TABLE IF NOT EXISTS Department (
        departmentID VARCHAR(25),
        name VARCHAR(25),
        studentCount INT,
        professorCount INT,
        majorOffered VARCHAR(25),
        PRIMARY KEY (departmentID)
        )
        ''',

    "ResidenceHall":
        '''
        CREATE TABLE IF NOT EXISTS ResidenceHall (
        roomNo INT,
        PRIMARY KEY (roomNo)
        )
        ''',

    "Students":
        '''
        CREATE TABLE IF NOT EXISTS Students (
        studentID CHAR(7),
        fname VARCHAR(25),
        lname VARCHAR(25),
        gradYear INT,
        departmentID VARCHAR(25),
        roomNo INT,
        PRIMARY KEY (studentID),
        FOREIGN KEY (departmentID) REFERENCES Department(departmentID),
        FOREIGN KEY (roomNo) REFERENCES ResidenceHall(roomNo)
        )
        ''',

    "Professor":
        '''
        CREATE TABLE IF NOT EXISTS Professor (
        professorID CHAR(7),
        fname VARCHAR(25),
        lname VARCHAR(25),
        departmentID VARCHAR(25) NOT NULL,
        PRIMARY KEY (professorID),
        FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
        )
        ''',

    "Course":
        '''
        CREATE TABLE IF NOT EXISTS Course (
        courseID VARCHAR(10),
        semester VARCHAR(10),
        credit INT,
        registerNum INT,
        departmentID VARCHAR(25),
        PRIMARY KEY (courseID, semester),
        FOREIGN KEY (departmentID) REFERENCES Department(departmentID)
        )
        ''',

    "Classroom":
        '''
        CREATE TABLE IF NOT EXISTS Classroom (
        roomCap INT,
        buildingNo INT,
        roomNo INT,
        PRIMARY KEY (buildingNo, roomNo)
        )
        ''',


    "courseProfessor":
        '''
        CREATE TABLE IF NOT EXISTS courseProfessor(
        courseID VARCHAR(10),
            semester VARCHAR(10),
        professorID CHAR(7),
        PRIMARY KEY(courseID,semester,professorID),
        FOREIGN KEY (courseID,semester) REFERENCES Course(courseID,semester),
        FOREIGN KEY (professorID) REFERENCES Professor(professorID)
        )
        ''',

    "courseClassroom":
        '''
        CREATE TABLE IF NOT EXISTS courseClassroom(
        courseID VARCHAR(10),
            semester VARCHAR(10),
            roomCap INT,
            buildingNo INT,
            roomNo INT,
            PRIMARY KEY(courseID,semester),
            FOREIGN KEY (courseID,semester) REFERENCES Course(courseID,semester),
            FOREIGN KEY (buildingNo, roomNo) REFERENCES Classroom(buildingNo, roomNo)
        )
        ''',

    "courseStudent":
        '''
        CREATE TABLE IF NOT EXISTS courseStudent(
        courseID VARCHAR(10),
        semester VARCHAR(10),
        studentID CHAR(7),
        PRIMARY KEY (courseID, semester, studentID),
        FOREIGN KEY (courseID, semester) REFERENCES Course(courseID, semester),
        FOREIGN KEY (studentID) REFERENCES Students(studentID)
        )
        ''',

    "Grades":
        '''
        CREATE TABLE IF NOT EXISTS Grades(
        courseGrade CHAR(1),
        courseMarks INT,
        semester VARCHAR(10),
        courseID VARCHAR(10),
        studentID CHAR(7),
        PRIMARY KEY (studentID,courseID,semester),
        FOREIGN KEY (studentID) REFERENCES Students(studentID),
        FOREIGN KEY (courseID,semester) REFERENCES Course(courseID,semester)
        )
        '''

}

def insert_data(df, table_name):
    placeholders = ', '.join(['%s'] * len(df.columns))
    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    for i, row in df.iterrows():
        print("row :",tuple(row))
        cursor.execute(sql, tuple(row))

    conn.commit()


for table, sql_command in create_table_commands.items():
    print("---------")
    print(f"table : {table}\nsql_command : {sql_command}")
    cursor.execute(sql_command)
for sheet_name in xl.sheet_names:
    df = xl.parse(sheet_name)
    insert_data(df, sheet_name)

conn.commit()
conn.close()