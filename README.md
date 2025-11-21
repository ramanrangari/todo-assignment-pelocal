Install Dependencies
pip install -r requirements.txt

Initialize Database
python db_init.py

Run the Application
python app.py

API Documentation

Health Check
1. GET /health
response:
{
  "status": "ok"
}

GET /api/tasks
Response
{
  "tasks": [
    {
      "id": 1,
      "title": "Sample Task",
      "description": "Do something",
      "due_date": "2025-11-25",
      "status": "pending",
      "created_at": "2025-11-20 12:00:00",
      "updated_at": "2025-11-20 12:00:00"
    }
  ]
}



GET /api/tasks/{id}

{
  "task": {
    "id": 1,
    "title": "Sample Task",
    "description": "Test",
    "due_date": "2025-11-25",
    "status": "pending"
  }
}

POST /api/tasks
Request Body

{
  "title": "Buy groceries",
  "description": "Milk, Eggs, Bread",
  "due_date": "2025-11-25",
  "status": "pending"
}


PATCH /api/tasks/{id}

{
  "status": "done",
  "title": "Buy groceries updated"
}

PUT /api/tasks/{id}

{
  "title": "Updated Task",
  "description": "New details",
  "due_date": "2025-11-28",
  "status": "in_progress"
}

DELETE /api/tasks/{id}
