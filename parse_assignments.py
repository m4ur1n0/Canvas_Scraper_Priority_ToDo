import json
import logging
import requests
import config
from bs4 import BeautifulSoup
from datetime import datetime
import json_uploader
import pytz

api_token = config.canvas_api_token
canvas_domain = "canvas.instructure.com"
user_id = "18760000000000504"
course_id = "18760000000178372"


# def get_total_possible_points(course_id, access_token, domain):
#     url = f"https://{domain}/api/v1/courses/{course_id}/total_scores"
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         total_scores = response.json()
#         total_possible_points = total_scores.get('total_scores', {}).get('possible')
#         return total_possible_points
#     else:
#         print(f"Failed to retrieve total possible points. Status code: {response.status_code}")
#         return None

def get_courses(api_token, domain):
    # takes in an api_token and the instructure domain
    # returns a dictionary of { course_id : course_name } of ONLY THE ACTIVE COURSES

    url = f"https://{domain}/api/v1/courses"
    headers = {"Authorization": f"Bearer {api_token}"}
    params = {"enrollment_state": "active"}

    response = requests.get(url, headers=headers, params=params)

    courses_dict = {}

    if response.status_code == 200:
        courses = response.json()
        with open("datadump.json", "w") as jj:
            json.dump(courses, jj, indent=4)
        for course in courses:
            try:
                # GET COURSE NAME
                course_id = course['id']
                course_name = course['name']
                # print(f"Course ID: {course_id}, Course Name: {course_name}")
                courses_dict[course_id] = {"name" : course_name}
                

            except Exception as e:
                print(e)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

    return courses_dict

def get_assignments(api_token, domain, course_id, course_dict):
    url = f"https://{domain}/api/v1/courses/{course_id}/assignments"
    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.get(url, headers=headers)

    # assignments_dict maps { assignment_id : (assignment_name, due_date, description, points_possible) }
    assignments_dict = {}

    if response.status_code == 200:
        try:
            assignments = response.json()
            for assignment in assignments:
                soup = BeautifulSoup(assignment['description'], 'html.parser')
                # print(f"Assignment ID: {assignment['id']}, Assignment Name: {assignment['name']}\nDue Date: {assignment['due_at']}\nDescription: {soup.get_text()}\nPoints Possible: {assignment['points_possible']}\n\n")

                # LEAVE IN ISO FORMAT TO BE PARSED LATER
                due_date = assignment['due_at']

                # points need to go in the course dictionary regardless of assignment due date -- calculating a standard
                points = assignment['points_possible']
                if points:
                    course_dict['grade_values'].append(points)
                else:
                    course_dict['grade_values'].append(0)

                if due_date:
                    # ignore any assignments without a due date
                    date_check = datetime.fromisoformat(due_date)
                    today = datetime.now(pytz.utc)

                    if today < date_check:
                        # ignore any assignments whose due dates have passed
                        id = assignment['id']
                        assignments_dict[id] = {'name' : assignment['name'], 'due_date' : due_date, 'description' : soup.get_text(), 'points' : points, 'course_id' : course_id}
                        # we only append assignment ids to course_Dict if the assignment is valid (yet to be completed)
                        course_dict['assignment_ids'].append(id)
                
        except Exception as e:
            logging.error(e)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    return assignments_dict


def get_all_assignments_from_all_courses(api_token, domain):
    # takes in an api_token and a domain
    # returns a tuple of dictionaries:
    # ({ course_id : course_name } , { course_id : [list, of, assignment_ids] } , { assignment_id : (assignment_name, due_date, description, points_possible) }

    cid_to_info = get_courses(api_token=api_token, domain=domain) # ACTIVE COURSES ONLY
    aids_to_info = {}

    for course_id in cid_to_info:
        
        cid_to_info[course_id]['assignment_ids'] = []
        cid_to_info[course_id]['grade_values'] = []

        course_assgts_info = get_assignments(api_token=api_token, domain=domain, course_id=course_id, course_dict=cid_to_info[course_id])
        aids_to_info.update(course_assgts_info)



    
    # change the set to a list for json serialization

    json_uploader.overwrite_json("json_out/course_ids_to_info.json", cid_to_info)
    # json_uploader.overwrite_json("json_out/course_id_to_assignment_ids.json", cid_to_aids)
    json_uploader.overwrite_json("json_out/assignment_ids_to_info.json", aids_to_info)



get_all_assignments_from_all_courses(api_token, canvas_domain)

# get_courses(api_token, canvas_domain)