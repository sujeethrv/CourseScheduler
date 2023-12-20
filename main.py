import sqlite3
import mysql.connector
from sqlalchemy import create_engine
import pdb
valid_tables = ['Department', 'ResidenceHall', 'Students', 'Professor', 'Course', 'Classroom', 'courseProfessor', 'courseClassroom', 'courseStudent', 'Grades']

def register_student(conn, student_id, fname, lname, department_id, grad_year, room_no):
    """
    Registers a new student in the university.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): Unique identifier for the student.
    fname (str): First name of the student.
    lname (str): Last name of the student.
    department_id (str): Department ID the student.
    grad_year (int): Graduation year of the student.
    room_no (int): Room number assigned to the student.

    Returns:
    str: Success message if registration is successful, otherwise error message.
    """
    # pdb.set_trace()
    cursor = conn.cursor()
    # cursor.execute("BEGIN")
    try:
        if not isinstance(student_id, str) or len(student_id) != 7:
            # cursor.execute("ROLLBACK")
            return "Invalid student ID format. It must be a 7-character string."

        if not (isinstance(grad_year, int) and 2010<=grad_year) or not isinstance(room_no, int):
            # cursor.execute("ROLLBACK")
            return "Graduation year and room number must be valid integers."

        if not fname or not isinstance(fname, str):
            return "First name is required and must be a string."

        if not lname or not isinstance(lname, str):
            return "Last name is required and must be a string."

        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID already exists."

        cursor.execute("SELECT * FROM Department WHERE departmentID = %s", (department_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Department ID does not exist."

        cursor.execute("SELECT * FROM ResidenceHall WHERE roomNo = %s", (room_no,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Room number does not exist."

        cursor.execute("SELECT * FROM Students WHERE roomNo = %s", (room_no,))
        if cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Room is already occupied by another student"
        
        cursor.execute("BEGIN")
        cursor.execute("INSERT INTO Students(studentID, fname, lname, gradYear, departmentID, roomNo) VALUES (%s, %s, %s, %s, %s, %s)", (student_id, fname, lname, grad_year, department_id, room_no))
        cursor.execute("UPDATE Department SET studentCount = studentCount + 1 WHERE departmentID = %s", (department_id,))
        
        cursor.execute("COMMIT")
        return "Student registered successfully."
    except sqlite3.Error as e:
        # cursor.execute("ROLLBACK")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occurred: {e}"

def register_student_for_course(conn, course_id, semester, student_id):
    """
    Registers a student for a specific course.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    course_id (str): ID of the course.
    semester (str): Semester for the course.
    student_id (str): ID of the student.

    Returns:
    str: Success message if operation is successful, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        # cursor.execute("BEGIN")
        if not isinstance(student_id, str) or len(student_id) != 7:
            # cursor.execute("ROLLBACK")
            return "Invalid student ID format. It must be a 7-character string."
        
        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."

        # Check if the student is already registered for this course in this semester
        cursor.execute("SELECT * FROM courseStudent WHERE courseID = %s AND semester = %s AND studentID = %s", (course_id, semester, student_id))
        if cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Student is already registered for this course in this semester."


        cursor.execute("SELECT registerNum FROM Course WHERE courseID = %s AND semester = %s", (course_id, semester))
        registration_data = cursor.fetchone()
        if not registration_data:
            # cursor.execute("ROLLBACK")
            return "Error: Course not found."

        registered_num = registration_data[0]

        cursor.execute("SELECT roomCap FROM courseClassroom WHERE courseID = %s AND semester = %s", (course_id, semester))
        room_data = cursor.fetchone()
        if not room_data:
            # cursor.execute("ROLLBACK")
            return "Error: Classroom details not found for the course."

        room_capacity = room_data[0]

        if registered_num >= room_capacity:
            # cursor.execute("ROLLBACK")
            return "Error: Classroom capacity exceeded."

        cursor.execute("BEGIN")
        # Register student for the course
        cursor.execute("UPDATE Course SET registerNum = registerNum + 1 WHERE courseID = %s AND semester = %s", (course_id, semester))
        cursor.execute("INSERT INTO courseStudent(courseID, semester, studentID) VALUES (%s, %s, %s)", (course_id, semester, student_id))
        cursor.execute("INSERT INTO Grades(courseGrade, courseMarks, semester, courseID, studentID) VALUES (%s, %s, %s, %s, %s)", ("F", 0, semester, course_id, student_id))#INITIAL GRADE WILL BE 0 AND MARKS WILL BE 0

        cursor.execute("COMMIT")
        return "Student registered for the course successfully."
    except sqlite3.Error as e:
        # cursor.execute("ROLLBACK")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occurred: {e}"

def withdrawing_a_student(conn, student_id):
    """
    Withdrawing a student from the university.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): ID of the student.

    Returns:
    str: Success message if operation is successful, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        # cursor.execute("BEGIN")

        if len(student_id) != 7: # not isinstance(student_id, str) or
            # cursor.execute("ROLLBACK")
            return "Invalid student ID format. It must be a 7-character string."
        
        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."

        cursor.execute("SELECT departmentID FROM Students WHERE studentID = %s", (student_id,))
        department_data = cursor.fetchone()
        department_num = department_data[0]

        cursor.execute("BEGIN")

        cursor.execute("DELETE FROM Grades WHERE studentID = %s", (student_id,))
        cursor.execute("DELETE FROM courseStudent WHERE studentID = %s", (student_id,))
        cursor.execute("UPDATE Department SET studentCount = studentCount-1 WHERE departmentID = %s", (department_num,))
        cursor.execute("DELETE FROM Students WHERE studentID = %s", (student_id,))
                
        # cursor.execute("UPDATE Department SET studentCount = studentCount-1 WHERE departmentID = %s", (department_num,))
        # cursor.execute("DELETE FROM courseStudent WHERE studentID = %s", (student_id,))
        # cursor.execute("DELETE FROM Students WHERE studentID = %s", (student_id,))
        cursor.execute("COMMIT")
        return "Student has been removed from the University"
    except sqlite3.Error as e:
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occur: {e}"


def drop_student_course(conn, course_id, semester, student_id):
    """
    Drops a student from a specific course. 

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    course_id (str): ID of the course.
    semester (str): Semester for the course.
    student_id (str): ID of the student.

    Returns:
    str: Success message if operation is successful, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        # cursor.execute("BEGIN")

        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."
        
        cursor.execute("SELECT * FROM courseStudent WHERE courseID = %s AND semester = %s AND studentID = %s", (course_id, semester, student_id))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Student is not registered for this course in this semester."

        else:
            cursor.execute("BEGIN")
            cursor.execute("UPDATE Course SET registerNum = registerNum - 1 WHERE CourseID = %s", (course_id,))
            cursor.execute("DELETE FROM courseStudent WHERE courseID = %s AND semester = %s AND studentID = %s", (course_id, semester, student_id))
            cursor.execute("SELECT SUM(Course.credit) FROM courseStudent LEFT JOIN Course ON courseStudent.courseID = Course.courseID WHERE courseStudent.studentID = %s AND courseStudent.semester = %s", (student_id, semester))            
            totalCredits = cursor.fetchone()[0]             
            if (totalCredits is None or totalCredits < 3):
                cursor.execute("ROLLBACK")
                return "Insufficient credits after dropping the course."
            else:          
                cursor.execute("COMMIT")
                return "Student has been dropped from course successfully."
    except sqlite3.Error as e:
        # cursor.execute("ROLLBACK")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occurred: {e}"


def student_major_switch(conn, student_id, major):
    """
    Switches a student from one major to a new one.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): ID of the student.
    major (str): new department of the student. 

    Returns:
    str: Success message if operation is successful, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        if not isinstance(student_id, str) or len(student_id) != 7:
            # cursor.execute("ROLLBACK")
            return "Invalid student ID format. It must be a 7-character string."
        
        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."
        
        cursor.execute("SELECT departmentID from Department WHERE departmentID = %s", (major,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Invalid major."

        cursor.execute("SELECT departmentID FROM Students WHERE studentID = %s", (student_id, ))
        departmentCheck = cursor.fetchone()
        if departmentCheck:
            if departmentCheck[0] == major:
                return "Error: Student is already enrolled in this major."
        
        cursor.execute("BEGIN")
        
        cursor.execute("SELECT departmentID FROM Students WHERE studentID = %s", (student_id,))
        department_data = cursor.fetchone()
        
        if department_data: 
            department_num = department_data[0]
            cursor.execute("UPDATE Department SET studentCount = studentCount-1 WHERE departmentID = %s", (department_num,))
        
        
        cursor.execute("UPDATE Students SET departmentID = %s WHERE studentID = %s", (major, student_id))
        cursor.execute("UPDATE DEPARTMENT SET studentCount = studentCount+1 WHERE departmentID = %s", (major,))

        cursor.execute("COMMIT")
        return "Students has has been switched majors succesfully."
    except sqlite3.Error as e:
        # cursor.execute("ROLLBACK")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occurred: {e}"

def comprehensive_report(conn, student_id, semester):
    """
    Retrieves and prints a comprehensive student report including course details, professors, classroom locations, and department information.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): Unique identifier for the student.
    semester (str): Semester for the course.

    Returns:
    str: Success message if the transcript is printed successfully, otherwise error message.
    """
    cursor = conn.cursor()
    try:

        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."
    
        cursor.execute("""
            SELECT s.fname, s.lname, c.courseID, g.courseGrade, g.courseMarks, 
                   p.fname AS pfname, p.lname AS plname, 
                   cl.buildingNo, cl.roomNo, d.name AS departmentName
            FROM courseStudent cs
            JOIN Students s ON cs.studentID = s.studentID
            JOIN Course c ON cs.courseID = c.courseID AND cs.semester = c.semester
            JOIN Grades g ON cs.courseID = g.courseID AND cs.semester = g.semester AND cs.studentID = g.studentID
            JOIN courseProfessor cp ON cs.courseID = cp.courseID AND cs.semester = cp.semester
            JOIN Professor p ON cp.professorID = p.professorID
            JOIN courseClassroom cc ON cs.courseID = cc.courseID AND cs.semester = cc.semester
            JOIN Classroom cl ON cc.buildingNo = cl.buildingNo AND cc.roomNo = cl.roomNo
            JOIN Department d ON c.departmentID = d.departmentID
            WHERE cs.studentID = %s AND cs.semester = %s
        """, (student_id, semester))
        rows = cursor.fetchall()

        if not rows:
            return "No data found for the specified student and semester."

        # Printing the report
        report = f"\nComprehensive Report for {student_id} - {semester}\n"
        report += f"{'Course ID':<10} {'Grade':<6} {'Marks':<6} {'Professor':<25} {'Classroom':<15} {'Department':<25}\n"
        report += "-" * 80 + "\n"

        for row in rows:
            fname, lname, course_id, grade, marks, pfname, plname, building, room, department = row
            classroom = f"Bldg {building}, Rm {room}"
            report += f"{course_id:<10} {grade:<6} {marks:<6} {pfname:<10} {plname:<15} {classroom:<15} {department:<25}\n"

        return report
    except sqlite3.Error as e:
        return f"SQL error occurred: {e}"



def get_student_transcript_sorted_by_marks(conn, student_id, order):
    """
    Retrieves and prints the transcript for the specified student, sorted by course marks.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): Unique identifier for the student.
    order (str): DESC or ASC order of output.

    Returns:
    str: Success message if the transcript is printed successfully, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        if (order != "ASC" and order != "DESC"):
            return "Error: Order is unknown. Use ASC or DESC"

        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."
        
        query = f"""
            SELECT s.studentID, s.fname, s.lname, g.courseID, g.semester, g.courseMarks, g.courseGrade
            FROM Grades g 
            LEFT JOIN Students s ON g.studentID = s.studentID 
            LEFT JOIN Course c ON g.courseID = c.courseID 
            WHERE g.studentID = %s 
            ORDER BY g.courseMarks {order}
            """
        cursor.execute(query, (student_id,))
        rows = cursor.fetchall()
        
        if not rows:
            return "No transcript records found for the student."

        print(f"Transcript for student {student_id}:")
        header = ("Student ID", "First Name", "Last Name", "Course ID", "Semester", "Marks", "Grade")
        print(f"{header[0]:<12} {header[1]:<15} {header[2]:<15} {header[3]:<10} {header[4]:<10} {header[5]:<6} {header[6]:<5}")
        print("-" * 90)


        for row in rows:
            student_id, fname, lname, course_id, semester, marks, grade = row
            print(f"{student_id:<12} {fname:<15} {lname:<15} {course_id:<10} {semester:<10} {marks:<6} {grade:<5}")


        
        return "Transcript printed successfully."
    except sqlite3.Error as e:
        return f"SQL error occurred: {e}"


def display_student_semester_schedule(conn, student_id, semester):
    """
    Displays the semester schedule for a specified student.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    student_id (str): ID of the student.
    semester (str): Semester for which the schedule is to be displayed.

    Returns:
    str: Success message if the schedule is displayed successfully, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Students WHERE studentID = %s", (student_id,))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Student ID does not exist."

        cursor.execute(""" 
                       SELECT cs.courseID, cp.professorID, cc.buildingNo, cc.roomNo 
                       FROM courseStudent cs LEFT JOIN Course c ON cs.courseID = c.courseID LEFT JOIN courseProfessor cp ON cs.courseID = cp.courseID AND cs.semester = cp.semester LEFT JOIN courseClassroom cc ON cs.courseID = cc.courseID AND cs.semester = cc.semester 
                       WHERE cs.studentID = %s AND cs.semester = %s""", (student_id, semester))
        rows = cursor.fetchall()

        if not rows:
            return "No schedule records found for the student for the specified semester."

        print(f"Semester schedule for student {student_id} for {semester}:")
        header = ("Course ID", "Professor ID", "Building No", "Room No")
        print(f"{header[0]:<10} {header[1]:<15} {header[2]:<15} {header[3]:<10}")
        print("-" * 80)

        for row in rows:
            print(f"{row[0]:<10} {row[1]:<15} {row[2]:<15} {row[3]:<10}")

        return "Schedule displayed successfully."
    except sqlite3.Error as e:
        return f"SQL error occurred: {e}"

def list_students_in_course_sorted_by_grade(conn, course_id, semester):
    """
    Lists students enrolled in a specific course, sorted by their grades.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    course_id (str): ID of the course.
    semester (str): Semester of the course.

    Returns:
    str: Success message if the operation is successful, otherwise error message.
    """
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Course WHERE courseID = %s AND semester = %s", (course_id, semester))
        if not cursor.fetchone():
            # cursor.execute("ROLLBACK")
            return "Error: Course is not offered in this semester."
        
        cursor.execute("""
            SELECT s.studentID, s.fname, s.lname, g.courseGrade
            FROM Grades g
            JOIN Students s ON g.studentID = s.studentID
            WHERE g.courseID = %s AND g.semester = %s
            ORDER BY g.courseGrade ASC, s.lname ASC, s.fname ASC
        """, (course_id, semester))
        rows = cursor.fetchall()

        if not rows:
            return "No students found for the specified course."

        print(f"Students in course {course_id} for {semester}:")
        header = ("Student ID", "First Name", "Last Name", "Grade")
        print(f"{header[0]:<12} {header[1]:<15} {header[2]:<15} {header[3]:<6}")
        print("-" * 50)

        for row in rows:
            print(f"{row[0]:<12} {row[1]:<15} {row[2]:<15} {row[3]:<6}")

        return "Student list displayed successfully."
    except sqlite3.Error as e:
        return f"SQL error occurred: {e}"


def add_rooms_to_residence_hall(conn, n):
    """
    Adds new rooms to the ResidenceHall table.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    n (int): The number of new rooms to be added.

    Returns:
    str: Success message if rooms are added successfully, otherwise error message.
    """
    cursor = conn.cursor()
    try:

        if not isinstance(n, int) or n <= 0:
            return "Number of rooms to add must be a positive integer."

        cursor.execute("SELECT MAX(roomNo) FROM ResidenceHall")
        max_room_no = cursor.fetchone()[0]

        cursor.execute("BEGIN")
        for i in range(1, n + 1):
            new_room_no = max_room_no + i
            cursor.execute("INSERT INTO ResidenceHall(roomNo) VALUES (%s)", (new_room_no,))

        cursor.execute("COMMIT")
        return f"Successfully added {n} rooms to the Residence Hall."
    except sqlite3.Error as e:
        # cursor.execute("ROLLBACK")
        try:
            cursor.execute("ROLLBACK")
        except:
            pass
        return f"SQL error occurred: {e}"

def print_table_data(conn, table_name):
    """
    Prints data from the specified table.

    Args:
    conn (sqlite3.Connection): The connection object for database interaction.
    table_name (str): Name of the table to print.

    Returns:
    str: Success or error message.
    """
    cursor = conn.cursor()

    # valid_tables = ['Department', 'ResidenceHall', 'Students', 'Professor', 'Course', 'Classroom', 'courseProfessor', 'courseClassroom', 'courseStudent', 'Grades']
    
    if table_name not in valid_tables:
        return "Invalid table name."

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row)
            return "Table data printed successfully."
        else:
            return "No data found in the table."
    except sqlite3.Error as e:
        return f"SQL error occurred: {e}"


def main():
    host = 'localhost'
    database = 'courseSchedulerDB'
    user = 'root'
    password = 'Useme123'
    conn = mysql.connector.connect(host=host, database='courseschedulerdb', user=user, password=password)
    # conn = sqlite3.connect('courseSchedulerDB.db')
    # cursor = conn.cursor()

    while True:
        print("\nOptions:")
        print("1. Register a Student")
        print("2. Register Student for a Course")
        print("3. Withdrawing a Student")
        print("4. Dropping a Student's Course")
        print("5. Switching a Student's major")
        print("6. Display a Comprehensive student report")
        print("7. Get Student Transcript Sorted by Marks")
        print("8. Display Student's Semester Schedule")
        print("9. List Students in a Course Sorted by Grade")
        print("10. Add Rooms to Residence Hall")
        print("11. Print data or check existing records")
        print("12. Exit")
        # print("13. pdb")

        choice = input("Enter your choice: ")

        if choice == '1':
            student_id = input("Enter Student ID (7 characters): ")
            fname = input("Enter Student's First Name: ")
            lname = input("Enter Student's Last Name: ")
            department_id = input("Enter Department ID: ")
            
            try:
                grad_year = int(input("Enter Graduation Year (e.g., 2024): "))
            except ValueError:
                print("Invalid input for Graduation Year. Please enter a valid number.")
                continue

            try:
                room_no = int(input("Enter Room Number: "))
            except ValueError:
                print("Invalid input for Room Number. Please enter a valid number.")
                continue

            result = register_student(conn, student_id, fname, lname, department_id, grad_year, room_no)
            print(result)

        elif choice == '2':
            course_id = input("Enter Course ID: ")
            semester = input("Enter Semester (e.g., 'Spring-20'): ")
            student_id = input("Enter Student ID: ")

            result = register_student_for_course(conn, course_id, semester, student_id)
            print(result)

        elif choice == '3':
            student_id = input("Enter Student ID: ")

            result = withdrawing_a_student(conn, student_id)
            print(result)
        
        elif choice == '4':
            course_id = input("Enter Course ID: ")
            semester = input("Enter Semester (e.g., 'Spring-20'): ")
            student_id = input("Enter Student ID: ")

            result = drop_student_course(conn, course_id, semester, student_id)
            print(result)
        
        elif choice == '5':
            student_id = input("Enter Student ID: ")
            major = input("Enter new  Major: ")

            result = student_major_switch(conn, student_id, major)
            print(result)

        elif choice == '6':
            student_id = input("Enter Student ID: ")
            semester = input("Enter Semester (e.g., 'Spring-20'): ")

            result = comprehensive_report(conn, student_id, semester)
            print(result)

        elif choice == '7':
            student_id = input("Enter the Student ID to print the transcript: ")
            order = input("Enter the order the grades should be sorted by (DESC or ASC): ")
            result = get_student_transcript_sorted_by_marks(conn, student_id, order)
            print(result)

        elif choice == '8':
            student_id = input("Enter the Student ID: ")
            semester = input("Enter the Semester (e.g., 'Spring-20'): ")
            result = display_student_semester_schedule(conn, student_id, semester)
            print(result)

        elif choice == '9':
            course_id = input("Enter the Course ID: ")
            semester = input("Enter the Semester (e.g., 'Spring-20'): ")
            result = list_students_in_course_sorted_by_grade(conn, course_id, semester)
            print(result)

        elif choice == '10':
            try:
                n = int(input("Enter the number of new rooms to add: "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                continue

            result = add_rooms_to_residence_hall(conn, n)
            print(result)

        elif choice == '11':
            print("Relations/Tables : ",valid_tables)
            table_name = input("Enter the table name to print: ")
            result = print_table_data(conn, table_name)
            print(result)

        elif choice == '12':
            print("Exiting...")
            break
        # elif choice=='13':
        #     pdb.set_trace()
        else:
            print("Invalid choice. Please try again.")

    conn.close()

if __name__ == "__main__":
    main()
