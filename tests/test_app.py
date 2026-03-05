import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

# Fixture to reset the in-memory activities dict before each test for isolation
@pytest.fixture(autouse=True)
def reset_activities():
    global activities
    # Deep copy to handle nested dicts/lists
    original = copy.deepcopy(activities)
    yield
    # Reset to original state
    activities.clear()
    activities.update(original)

client = TestClient(app)

def test_get_activities_success():
    # Arrange: No special setup needed, activities are pre-populated
    
    # Act: Make GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check status and that all activities are returned
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0  # Assuming activities are not empty
    assert "Chess Club" in data  # Example check for a known activity

def test_signup_for_activity_success():
    # Arrange: Choose an activity and a new email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check success response and that participant was added
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1

def test_signup_for_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistentActivity"
    email = "student@mergington.edu"
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_for_activity_duplicate():
    # Arrange: Choose an activity and an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check 400 error for duplicate
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}

def test_unregister_from_activity_success():
    # Arrange: Choose an activity and an email already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    initial_participants = activities[activity_name]["participants"].copy()
    
    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check success response and that participant was removed
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1

def test_unregister_from_activity_not_found():
    # Arrange: Use a non-existent activity name
    activity_name = "NonExistentActivity"
    email = "student@mergington.edu"
    
    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check 404 error
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_from_activity_not_signed_up():
    # Arrange: Choose an activity and an email not signed up
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"  # Not in participants
    
    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check 400 error for not signed up
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not signed up"}