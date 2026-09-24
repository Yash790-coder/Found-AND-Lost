# Campus Lost & Found API

A FastAPI REST API backed by SQLite and SQLModel for reporting and managing campus lost-and-found items.

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run the API

```powershell
uvicorn main:app --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>.

The SQLite database is created as `lost_and_found.db` when the application starts.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/items` | Create a lost/found report |
| GET | `/items` | List all reports |
| GET | `/items/{item_id}` | Get one report |
| PUT | `/items/{item_id}` | Update a report |
| DELETE | `/items/{item_id}` | Delete a report |
| GET | `/items/status/{status}` | Filter by `Lost`, `Found`, or `Returned` |
| GET | `/items/category/{category}` | Filter by category |

Example request body:

```json
{
  "title": "Blue water bottle",
  "description": "Reusable bottle with a silver lid",
  "category": "Accessories",
  "location": "Library second floor",
  "reported_by": "Aisha Khan",
  "status": "Lost"
}
```

## Tests

```powershell
pytest -q
```

## Proof of work screenshots

Use `/docs` to execute and capture successful responses for:

1. `POST /items` showing `201 Created` and the returned item ID.
2. `GET /items` showing the created report.
3. `GET /items/{item_id}` showing the individual report.
4. `PUT /items/{item_id}` showing the updated status or details.
5. `DELETE /items/{item_id}` showing `204 No Content`.
6. `GET /items/status/Lost` or `/items/status/Found` showing filtered results.
7. `GET /items/category/Accessories` showing category-filtered results.

Save the screenshots in a `screenshots/` folder before pushing the project to GitHub.
