#!/usr/bin/env python3
import psycopg2
import logging 

def openConnection():

    database_name = "elec5620"
    userid = "postgres"
    passwd = "PASSword123."
    myHost = "elec5620.cdce2uw4szzi.ap-southeast-2.rds.amazonaws.com"  # RDS' Endpoint

    conn = None
    try:
        # connect to RDS PostgreSQL instance
        conn = psycopg2.connect(database=database_name, user=userid, password=passwd, host=myHost, port="5432")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        return conn

def check_login(user_id, password):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT firstName, lastName, role
            FROM users 
            WHERE user_id = %s AND password = %s
            """
            cursor.execute(query, (user_id, password))
            user = cursor.fetchone()

            if user:
                return {
                    'success': True,
                    'message': f'Login successful, welcome {user[0]} {user[1]}',
                    'role': user[2],
                    'userId': user_id
                }
            else:
                return None
    except psycopg2.Error as e:
        logging.error(f"Error fetching user: {e}")
        return None
    finally:
        conn.close() 

def get_projects():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT project_id, project_name
            FROM projects
            """
            cursor.execute(query)
            projects = cursor.fetchall()

            project_list = []
            for project in projects:
                project_list.append({
                    'Project_id': project[0],
                    'project_name': project[1]
                })

            return project_list
    except psycopg2.Error as e:
        logging.error(f"Error fetching projects: {e}")
        return None
    finally:
        conn.close()

def get_project_details(project_id):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Fetch project details including duration based on start_date and deadline
            query = """
            SELECT p.project_id, p.project_name, p.description, p.deadline, p.start_date,
                   SUM(e.salary * ep.hours_worked) AS total_earning, 
                   EXTRACT(EPOCH FROM (p.deadline - p.start_date)) / 3600 AS total_duration
            FROM projects p
            LEFT JOIN employee_project ep ON p.project_id = ep.project_id
            LEFT JOIN employee e ON e.employee_id = ep.employee_id
            WHERE p.project_id = %s
            GROUP BY p.project_id
            """
            cursor.execute(query, (project_id,))
            project = cursor.fetchone()

            if project:
                # Fetch employees working on the project
                employee_query = """
                SELECT e.employee_id 
                FROM employee_project ep
                JOIN employee e ON e.employee_id = ep.employee_id
                WHERE ep.project_id = %s
                """
                cursor.execute(employee_query, (project_id,))
                employees = [row[0] for row in cursor.fetchall()]

                return {
                    "id": str(project[0]),
                    "name": project[1],
                    "description": project[2],
                    "deadline": project[3].isoformat(),  # Convert to ISO 8601 format
                    "employees": employees,
                    "totalEarning": float(project[5]) if project[5] else 0.0,
                    "totalDuration": float(project[6]) if project[6] else 0.0  # Duration in hours
                }
            else:
                return None
    except psycopg2.Error as e:
        logging.error(f"Error fetching project details: {e}")
        return None
    finally:
        conn.close()

def get_teams():
    conn = openConnection()  
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            #Query the team table to get all team information
            query = """
            SELECT team_id, name
            FROM teams
            """
            cursor.execute(query)
            teams = cursor.fetchall()

            #Return the list of teams
            if teams:
                team_list = []
                for team in teams:
                    team_list.append({
                        'id': str(team[0]),  # convert to string
                        'name': team[1]
                    })
                
                return {
                    "teams": team_list
                }
            else:
                return {
                    "teams": []
                }
    except psycopg2.Error as e:
        logging.error(f"Error fetching teams: {e}")
        return None
    finally:
        conn.close()


def get_team_details(team_id):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Query to get the details of the team by team_id
            query = """
            SELECT id, name, description, total_earning, total_duration, team_efficiency
            FROM teams
            WHERE id = %s
            """
            cursor.execute(query, (team_id,))
            team = cursor.fetchone()

            if team:
                # Format the response as a dictionary with team details
                return {
                    'id': str(team[0]),  # Ensuring 'id' is returned as a string
                    'name': team[1],
                    'description': team[2],
                    'totalEarning': float(team[3]) if team[3] else 0.0,
                    'totalDuration': int(team[4]) if team[4] else 0,
                    'teamEfficiency': int(team[5]) if team[5] else 0
                }
            else:
                return None
    except psycopg2.Error as e:
        logging.error(f"Error fetching team details: {e}")
        return None
    finally:
        conn.close()

def get_financial_records():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Query to get financial records along with project name and employee details
            query = """
            SELECT fr.item_id, p.project_name, 
                   SUM(CASE WHEN fr.category = 'income' THEN fr.amount ELSE 0 END) AS earning,
                   SUM(CASE WHEN fr.category = 'expense' THEN fr.amount ELSE 0 END) AS cost,
                   e.firstname || ' ' || e.lastname AS employee_name,
                   fr."timestamp"
            FROM financial_records fr
            LEFT JOIN projects p ON fr.project_id = p.project_id
            LEFT JOIN employee e ON fr.employee_id = e.employee_id
            GROUP BY fr.item_id, p.project_name, e.firstname, e.lastname, fr."timestamp"
            """
            cursor.execute(query)
            records = cursor.fetchall()

            # Format the response as a list of dictionaries
            records_list = []
            for record in records:
                records_list.append({
                    'id': str(record[0]),  # item_id as string
                    'projectName': record[1],  # project_name
                    'earning': float(record[2]),  # earning (income)
                    'cost': float(record[3]),  # cost (expense)
                    'employeeName': record[4],  # employee name (firstname + lastname)
                    'timestamp': record[5].isoformat()  # ISO 8601 format
                })

            return {
                'records': records_list
            }
    except psycopg2.Error as e:
        logging.error(f"Error fetching financial records: {e}")
        return None
    finally:
        conn.close()


def get_psychological_assessments():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Query to get psychological assessments
            query = """
            SELECT psy_id, assessment, "timestamp"
            FROM psychological_assessments
            """
            cursor.execute(query)
            assessments = cursor.fetchall()

            # Format the response as a list of dictionaries
            assessments_list = []
            for assessment in assessments:
                assessments_list.append({
                    'id': str(assessment[0]),  # psy_id as a string
                    'assessment': assessment[1],  # assessment text
                    'timestamp': assessment[2].isoformat()  # ISO 8601 formatted timestamp
                })

            return {
                'assessments': assessments_list
            }
    except psycopg2.Error as e:
        logging.error(f"Error fetching psychological assessments: {e}")
        return None
    finally:
        conn.close()


def get_feedback():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None
    logging.info("Connected to the database successfully")
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT f.feedback_id, u.firstname || ' ' || u.lastname AS employee_name, 
                   f.feedback_content, f."timestamp"
            FROM feedback f
            JOIN employee e ON f.employee_id = e.employee_id
            JOIN users u ON e.employee_id = u.user_id
            """
            cursor.execute(query)
            feedbacks = cursor.fetchall()

            feedback_list = []
            for feedback in feedbacks:
                feedback_list.append({
                    'id': str(feedback[0]), 
                    'employeeName': feedback[1],  
                    'content': feedback[2],  
                    'timestamp': feedback[3].isoformat()  
                })

            return {
                'employees': feedback_list, 
                'success': True
            }
    except psycopg2.Error as e:
        logging.error(f"Error fetching feedback: {e}")
        return None
    finally:
        conn.close()


def get_clock_in_records():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT cir.clock_in_id, p.project_name, cir.start_time, cir.end_time, cir.duration
            FROM clock_in_records cir
            JOIN projects p ON cir.project_id = p.project_id
            """
            cursor.execute(query)
            records = cursor.fetchall()

            records_list = []
            for record in records:
                records_list.append({
                    'id': str(record[0]), 
                    'projectName': record[1],  
                    'startTime': record[2].isoformat(),  
                    'endTime': record[3].isoformat(), 
                    'duration': float(record[4]) 
                })

            return {
                'records': records_list
            }
    except psycopg2.Error as e:
        logging.error(f"Error fetching clock-in records: {e}")
        return None
    finally:
        conn.close()


def get_employees():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return {'error': 'Failed to connect to the database'}

    try:
        with conn.cursor() as cursor:
            query = """
            SELECT e.employee_id, u.firstname || ' ' || u.lastname AS name, 
                   u.age, u.gender, u.role, e.total_work_duration, e.number_of_projects
            FROM employee e
            JOIN users u ON e.employee_id = u.user_id
            """
            cursor.execute(query)
            employees = cursor.fetchall()

            if not employees: 
                return {'error': 'No employees found'}

            employees_list = [
                {
                    'id': str(employee[0]),
                    'name': employee[1],
                    'age': int(employee[2]) if employee[2] is not None else None,
                    'gender': employee[3] if employee[3] is not None else 'N/A',
                    'role': employee[4] if employee[4] is not None else 'N/A',
                    'totalWorkDuration': float(employee[5]) if employee[5] is not None else 0.0,
                    'numberOfProjects': int(employee[6]) if employee[6] is not None else 0
                }
                for employee in employees
            ]
            logging.debug(f"Employees List: {employees_list}") 
            return {'employees': employees_list,
                    'success': True}
    
    except psycopg2.Error as e:
        logging.error(f"Error fetching employees: {e}")
        return {'error': f"Error fetching employees: {str(e)}"}
    
    finally:
        if conn:
            conn.close()




from datetime import datetime, timedelta

def get_employee_time_analysis():
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            #duration in hours:work_duration := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time)) / 3600;
            query = """
            SELECT u.user_id, u.firstname || ' ' || u.lastname AS name, 
                   u.date AS start_date, SUM(cir.duration) AS total_hours
            FROM users u
            LEFT JOIN clock_in_records cir ON u.user_id = cir.employee_id
            WHERE u.role = 'employee'
            GROUP BY u.user_id, u.firstname, u.lastname, u.date
            """
            cursor.execute(query)
            employees = cursor.fetchall()

            current_date = datetime.now()

            employees_list = []
            for employee in employees:
                employee_id = employee[0]
                name = employee[1]
                start_date = employee[2]
                total_hours = float(employee[3]) if employee[3] else 0.0

                # Calculate the total hours worked in the most recent 7-day and 30-day periods
                cursor.execute("""
                SELECT SUM(duration) 
                FROM clock_in_records 
                WHERE employee_id = %s AND start_time >= %s
                """, (employee_id, current_date - timedelta(days=7)))
                weekly_hours = cursor.fetchone()[0] or 0.0

                cursor.execute("""
                SELECT SUM(duration) 
                FROM clock_in_records 
                WHERE employee_id = %s AND start_time >= %s
                """, (employee_id, current_date - timedelta(days=30)))
                monthly_hours = cursor.fetchone()[0] or 0.0

                employees_list.append({
                    'id': str(employee_id),
                    'name': name,
                    'weeklyHours': round(weekly_hours, 2), 
                    'monthlyHours': round(monthly_hours, 2) 
                })

            return {
                'employees': employees_list
            }
    except psycopg2.Error as e:
        logging.error(f"Error fetching employee time analysis: {e}")
        return None
    finally:
        conn.close()



def create_project(project_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        # Create a cursor to execute SQL queries
        with conn.cursor() as cursor:
            # Insert project data into the projects table
            query = """
            INSERT INTO projects (project_name, description, deadline)
            VALUES (%s, %s, %s)
            RETURNING project_id
            """
            cursor.execute(query, (project_data['name'].lower(), project_data['description'].lower(), project_data['deadline']))
            project_id = cursor.fetchone()[0]

            # Insert employee-project relationships into the employee_project table
            for employee_id in project_data['employees'].split(','):
                cursor.execute("INSERT INTO employee_project (employee_id, project_id) VALUES (%s, %s)", 
                               (employee_id.strip().lower(), project_id))

            # Commit after all employee-project relations are inserted
            conn.commit()

            # Success response
            response = {
                "success": True,
                "message": "Project created successfully",
                "projectId": project_id
            }
            print(response)
            return project_id

    except psycopg2.Error as e:
        logging.error(f"Error creating project: {e}")
        response = {
            "success": False,
            "message": "Failed to create project",
            "projectId": None
        }
        print(response)
        return None

    finally:
        conn.close()



def update_project(project_id, project_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None
    try:
        with conn.cursor() as cursor:
            # Update project details in the projects table
            query = """
            UPDATE projects
            SET project_name = %s, description = %s, deadline = %s
            WHERE project_id = %s
            """
            cursor.execute(query, (project_data['name'].lower(), project_data['description'].lower(), project_data['deadline'], project_id))

            # Delete existing employee-project relationships
            cursor.execute("DELETE FROM employee_project WHERE project_id = %s", (project_id,))

            # Insert updated employee-project relationships
            for employee_id in project_data['employees'].split(','):
                cursor.execute("INSERT INTO employee_project (employee_id, project_id) VALUES (%s, %s)", 
                               (employee_id.strip().lower(), project_id))

            conn.commit()
            response = {
                "success": True,
                "message": "Project updated successfully"
            }
            print(response)
            return True
    except psycopg2.Error as e:
        logging.error(f"Error updating project: {e}")
        response = {
            "success": False,
            "message": "Failed to update project"
        }
        return response
    finally:
        conn.close()

def create_team(team_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Insert team data into the teams table
            query = """
            INSERT INTO teams (name, description)
            VALUES (%s, %s)
            RETURNING id
            """
            cursor.execute(query, (team_data['name'].lower(), team_data['description'].lower()))
            team_id = cursor.fetchone()[0]
            for employee_id in team_data['employees'].split(','):
                cursor.execute("INSERT INTO team_employee (employee_id, team_id) VALUES (%s, %s)", 
                               (employee_id.strip().lower(), team_id))
            conn.commit()
            response = {
                "success": True,
                "message": "Team created successfully",
                "teamId": team_id
            }
            print(response)
            return team_id
    except psycopg2.Error as e:
        logging.error(f"Error creating team: {e}")
        response = {
            "success": False,
            "message": "Failed to create team",
            "teamId": None
        }
        print(response)
        return None
    finally:
        conn.close()

def update_team(team_id, team_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        with conn.cursor() as cursor:
            # Update team details in the teams table
            query = """
            UPDATE teams
            SET name = %s, description = %s
            WHERE id = %s
            """
            cursor.execute(query, (team_data['name'].lower(), team_data['description'].lower(), team_id))
            cursor.execute("DELETE FROM team_employee WHERE team_id = %s", (team_id,))
            for employee_id in team_data['employees'].split(','):
                cursor.execute("INSERT INTO team_employee (employee_id, team_id) VALUES (%s, %s)", 
                               (employee_id.strip().lower(), team_id))
            conn.commit()
            response = {
                "success": True,
                "message": "Team updated successfully"
            }
            print(response)
            return True
    except psycopg2.Error as e:
        logging.error(f"Error updating team: {e}")
        response = {
            "success": False,
            "message": "Failed to update team"
        }
        return response
    finally:
        conn.close()

def add_financial_record(record_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None

    try:
        # Create a cursor to execute SQL queries
        with conn.cursor() as cur:
            # Get the project ID from the project name
            get_project_id_query = """
            SELECT project_id FROM projects WHERE project_name = %s
            """
            cur.execute(get_project_id_query, (record_data['projectName'].lower(),))
            project_id = cur.fetchone()
            
            if project_id is None:
                return {
                    "success": False,
                    "message": f"Project '{record_data['projectName']}' not found.",
                    "recordId": None
                }
            project_id = project_id[0]
            # Initialize a list to store newly added record IDs
            added_record_ids = [] 
            # Check if earning is present and non-zero
            if 'earning' in record_data and record_data['earning'] > 0:
                # Insert the financial record into the financial_records table
                cur.execute("""
                INSERT INTO financial_records (project_id, amount, category, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING item_id
                """, (project_id, record_data['earning'], 'Income', record_data['timestamp']))
                record_id = cur.fetchone()[0]
                added_record_ids.append(record_id)
            #check if cost is present and non-zero
            if 'cost' in record_data and record_data['cost'] > 0:
                # Insert the financial record into the financial_records table
                cur.execute("""
                INSERT INTO financial_records (project_id, amount, category, timestamp)
                VALUES (%s, %s, %s, %s)
                RETURNING item_id
                """, (project_id, record_data['cost'], 'Expense', record_data['timestamp']))
                record_id = cur.fetchone()[0]
                added_record_ids.append(record_id)
            # Commit the transaction
            conn.commit()
            if added_record_ids:
                # Prepare success response if records were added
                response = {
                    "success": True,
                    "message": "Financial record(s) added successfully",
                    "recordId": ', '.join(map(str, added_record_ids))  # List of added record IDs
                }
            else:
                # No records were added
                response = {
                    "success": False,
                    "message": "No financial records were added (earning or cost is 0).",
                    "recordId": None
                }
            
            return response
    except psycopg2.Error as e:
        logging.error(f"Error adding financial record: {e}")
        return {
            "success": False,
            "message": "Failed to add financial record",
            "recordId": None
        }
    finally:
        conn.close()

def submit_psychological_assessment(assessment_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None
    try:
         # Retrieve the current user's employee_id
        with conn.cursor() as cursor:
            # Insert the psychological assessment into the psychological_assessments table
            query = """
            INSERT INTO psychological_assessments (assessment, timestamp, employee_id)
            VALUES (%s, %s, %s)
            RETURNING psy_id
            """
            cursor.execute(query, (assessment_data['assessment'].lower(), assessment_data['timestamp'], assessment_data['userId']))
            assessment_id = cursor.fetchone()[0]
            conn.commit()
            response = {
                "success": True,
                "message": "Assessment submitted successfully",
                "assessmentId": assessment_id
            }
            return response
    except psycopg2.Error as e:
        logging.error(f"Error submitting psychological assessment: {e}")
        response = {
            "success": False,
            "message": "Failed to submit assessment",
            "assessmentId": None
        }
        return response
    finally:
        conn.close()

def submit_feedback(feedback_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None
    try:
        with conn.cursor() as cursor:
            # Insert the feedback into the feedback table
            query = """
            INSERT INTO feedback (feedback_content, timestamp, employee_id)
            VALUES (%s, %s, %s)
            RETURNING feedback_id
            """
            cursor.execute(query, (feedback_data['content'].lower(), feedback_data['timestamp'], feedback_data['userId']))
            feedback_id = cursor.fetchone()[0]
            conn.commit()
            response = {
                "success": True,
                "message": "Feedback submitted successfully",
                "feedbackId": feedback_id
            }
            return response
    except psycopg2.Error as e:
        logging.error(f"Error submitting feedback: {e}")
        response = {
            "success": False,
            "message": "Failed to submit feedback",
            "feedbackId": None
        }
        return response
    finally:
        conn.close()

# assign user_id by concatenating first letter of first name with last name
# initialize password as 'password' for all new employees
# split name into first name and last name, insert user_id, name, age, gender to the users table;
def add_employee(employee_data):
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return {'message': 'Failed to connect to the database', 'success': False}
    
    try:
        with conn.cursor() as cursor:
            name = employee_data['name']
            age = employee_data['age']
            gender = employee_data['gender']
            role = employee_data['role']
            salary = employee_data.get('salary', 40000)  
            password = 'password'  
            
            name_parts = name.split()
            first_name = ' '.join(name_parts[:-1])
            last_name = name_parts[-1] if len(name_parts) > 1 else ''
            user_id = first_name[0].lower() + last_name.lower() if last_name else first_name.lower()
            
            logging.info(f"Executing query: {insert_employee_query} with values: ({user_id}, 0, 0)")

            insert_user_query = """
            INSERT INTO users (user_id, firstname, lastname, age, salary, gender, role, password, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            """
            cursor.execute(insert_user_query, (user_id, first_name, last_name, age, salary, gender, role, password))

            insert_employee_query = """
            INSERT INTO employee (employee_id, total_work_duration, number_of_projects)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_employee_query, (user_id, 0, 0))  
            
            conn.commit()
            logging.info(f"Employee {user_id} inserted successfully.")
            
            return {'success': True, 'user_id': user_id}
    
    except psycopg2.Error as e:
        logging.error(f"Error adding employee: {e}")
        conn.rollback()  
        return {'message': f"Error adding employee: {str(e)}", 'success': False}
    
    finally:
        if conn:
            conn.close()



# def get_time_tracking_data():
#     # TODO: Implement logic to retrieve time tracking data
#     # 1. Connect to the database
#     # 2. Query the time tracking table to get all time tracking records
#     # 3. Return the list of time tracking data
#     conn = openConnection()
#     if not conn:
#         logging.error("Failed to connect to the database.")
#         return None
#     try:
#         with conn.cursor() as cursor:
#             query = """
#             SELECT cir.clock_in_id, p.project_name, cir.start_time, cir.end_time, cir.duration
#             FROM clock_in_records cir
#             JOIN projects p ON cir.project_id = p.project_id
#             """
#             cursor.execute(query)
#             records = cursor.fetchall()
#             records_list = []
#             for record in records:
#                 records_list.append({
#                     'id': str(record[0]), 
#                     'projectName': record[1],  
#                     'startTime': record[2].isoformat(),  
#                     'endTime': record[3].isoformat(), 
#                     'duration': float(record[4]) 
#                 })
#             return records_list
#     except psycopg2.Error as e:
#         logging.error(f"Error fetching time tracking data: {e}")
#         return None
#     finally:
#         conn.close()

# def add_time_tracking_record(record_data):
#     # TODO: Implement logic to add a time tracking record
#     # 1. Connect to the database
#     # 2. Insert record_data into the time tracking table
#     # 3. Return the ID of the newly created record
#     conn = openConnection()
#     if not conn:
#         logging.error("Failed to connect to the database.")
#         return None
#     try:
#         with conn.cursor() as cursor:
#             query = """
#             INSERT INTO projects (project_name)
#             VALUES (%s)
#             RETURNING project_id
#             """
#             cursor.execute(query, (record_data['projectName'].lower(),))
#             project_id = cursor.fetchone()[0]
#             query = """
#             INSERT INTO clock_in_records (project_id, start_time, end_time, duration)
#             VALUES (%s, %s, %s, %s)
#             RETURNING clock_in_id
#             """
#             cursor.execute(query, (project_id, record_data['startTime'], record_data['endTime'], record_data['duration']))
#             record_id = cursor.fetchone()[0]
#             conn.commit()
#             response = {
#                 "success": True,
#                 "message": "Time tracking record added successfully",
#                 "recordId": record_id
#             }
#             return response
#     except psycopg2.Error as e:
#         response = {
#             "success": False,
#             "message": "Failed to add time tracking record",
#             "recordId": None
#         }
#         return response
#     finally:
#         conn.close()


def submit_clock_in(clock_in_data):
    # TODO: Implement logic to submit a clock-in record
    # 1. Connect to the database
    # 2. Insert clock_in_data into the clock-in records table
    # 3. Return the ID of the newly created clock-in record
    conn = openConnection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return None
    try:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO clock_in_records (project_id, start_time, end_time, employee_id)
            VALUES (%s, %s, %s, %s)
            RETURNING clock_in_id
            """
            cursor.execute(query, (clock_in_data['projectId'], clock_in_data['startTime'], clock_in_data['endTime'], clock_in_data['userId']))
            record_id = cursor.fetchone()[0]
            conn.commit()
            response = {
                "success": True,
                "message": "Clock-in record submitted successfully",
                "recordId": record_id
            }
            return response
    except psycopg2.Error as e:
        logging.error(f"Error submitting clock-in record: {e}")
        response = {
            "success": False,
            "message": "Failed to submit clock-in record",
            "recordId": None
        }
        return response
