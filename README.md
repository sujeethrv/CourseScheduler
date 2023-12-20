# Course Scheduler: University Management System

## Overview
Course Scheduler is a robust University Management System tailored to streamline the administrative and academic management of universities. Developed by Timothy Zeng and Sujeeth Reddy Vummanthala, under the mentorship of Dong Xie for CMPSC 431W, this system is inspired by Penn State's Lionpath and is ideal for institutions seeking a new or improved management system.

## Detailed Overview
This section offers an in-depth look at the various aspects and capabilities of the Course Scheduler.

- **Comprehensive Database Structure**: The system includes 8 detailed tables for managing Student, Course, Professor, Department, Scheduling, Grade, Residence Hall, and Classroom information.
- **Diverse Functional Capabilities**: Features include student registration, course enrollment, major modification, meeting scheduling, and more.
- **Efficient Data Management**: Handles a variety of data types, suitable for bulk uploads and ongoing entry updates.
- **Schema Optimization**: Database structure refined to Boyce-Codd Normal Form (BCNF).
- **Powered by MySQL**: Utilizes the robustness and reliability of MySQL for database operations, ensuring data security and scalability.
- **User-Friendly Command-Line Interface**: Designed for simplicity and ease of use, facilitating seamless interaction with the database.


## Functionalities
1. **Register a Student**: Adds a new student to the system.
2. **Enroll in a Course**: Registers a student for a specific course.
3. **Withdraw a Student**: Removes a student from the university.
4. **Drop a Course**: Allows a student to drop a course, ensuring credit requirements are met.
5. **Change Major**: Modifies a student's major and department.
6. **Schedule Academic Meetings**: Organizes meetings based on student and professor performance.
7. **Generate Transcripts**: Produces academic records for students.
8. **View Semester Schedule**: Displays a student's course schedule for a semester.
9. **List Students in a Course**: Shows students enrolled in a course, sorted by grade.
10. **Add Rooms to Residence Hall**: Expands the accommodation capacity.


## Deployment
1. Navigate to the project directory.
2. Initialize the database: Run `python dataToDB.py`.
3. To interact with the database, run `python main.py`.
