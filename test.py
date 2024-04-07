import parse_assignments
import config
import requests

# print(parse_assignments.get_courses(config.api_token, config.canvas_domain))
def get_total_possible_points(course_id, access_token, domain):
    url = f"https://{domain}/api/v1/courses/{course_id}/total_scores"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        total_scores = response.json()
        print(total_scores)
        total_possible_points = total_scores.get('total_scores', {}).get('possible')
        return total_possible_points
    else:
        print(f"Failed to retrieve total possible points. Status code: {response.status_code}")
        return None
    
print(get_total_possible_points("18760000000209140", config.api_token, config.canvas_domain))