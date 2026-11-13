

# FastAPI + SQLAlchemy Learning Notes

## Personal Productivity & Learning Tracker --- Progress so far

These notes cover the concepts and implementation we have completed so
far. They are intended for revision: use the explanations, code, flow
diagrams, and self-check questions to reconstruct the reasoning rather
than simply memorising code.

---

## 1. What we are building

We are building a **Personal Productivity & Learning Tracker** backend
using FastAPI.

Our first feature is task management: - Create a task. - Store it
persistently. - Retrieve and eventually update or delete tasks.

We initially stored tasks in a Python dictionary. That worked while the
application was running, but the data disappeared when the server
restarted. We are replacing that temporary storage with SQLite.

### In-memory dictionary vs database

---

  In-memory dictionary                                              SQLite database

---

  Lives in application memory                                    Stored in a database file

  Data is lost when the process stops                        Data persists after restart

  Simple for an initial exercise       				   Suitable for persistent application data

No SQL queries needed               Data is accessed through database
                                      operations
------------------------------------------------

---

## 2. FastAPI foundations we used

### FastAPI application instance

```python
from fastapi import FastAPI

app = FastAPI()
```

- `FastAPI` is the class imported from the FastAPI package.
- `app` is the application instance.
- We attach routes/endpoints to this instance.

### A route / endpoint

```python
@app.get("/")
def home():
    return "Hello how are you!!"
```

- `@app.get("/")` registers a handler for HTTP GET requests to `/`.
- `home()` is the function FastAPI calls for that request.
- An **endpoint** is an API operation exposed at a particular path and
  HTTP method.
- HTTP is the communication protocol. JSON is a common
  request/response data format, but HTTP can carry other formats too.

### Pydantic request schemas

We use Pydantic models to validate and describe data entering or leaving
the API.

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str
```

When an endpoint declares `task: TaskCreate`, FastAPI reads the request
body, validates it against the schema, and supplies a Pydantic object to
the function.

For example, a request body could be:

```json
{
  "title": "Learn SQLAlchemy",
  "description": "Understand database integration with FastAPI"
}
```

If required fields are missing or have incompatible types, request
validation fails before the endpoint's main logic runs.

### `model_dump()`

```python
task_data = task.model_dump()
```

`model_dump()` converts a Pydantic model instance into a normal Python
dictionary. We used this in the earlier in-memory CRUD implementation.

### Response models

A response model describes and validates the shape of data returned by
an endpoint.

```python
class TaskResponse(TaskCreate):
    id: int
```

`TaskResponse` inherits `title` and `description` from `TaskCreate`, and
adds `id`.

We can use it like this:

```python
@app.post("/tasks", response_model=TaskResponse)
```

FastAPI uses the response model to validate and serialize the returned
data. It also helps document the response in OpenAPI/Swagger UI.

---

## 3. Why we moved to SQLite

The original implementation used a dictionary:

```python
tasks_db = {}
```

This was useful for learning CRUD: - POST created a task in the
dictionary. - GET read from it. - PUT replaced/updated an entry. -
DELETE removed an entry.

However, the dictionary only existed in the running Python process.
Restarting the server cleared it.

SQLite stores data in a local database file. We chose it to learn
persistence and database integration without needing to run a separate
database server.

Our configured database filename is `productivity.db`:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./productivity.db"
```

The `./` means the file is relative to the application's current working
directory.

> Check the filename in your actual connection URL. Earlier, `prod.db`
> was mentioned during setup; the later configured URL used
> `productivity.db`. The URL determines which file SQLAlchemy uses.

---

## 4. SQLAlchemy: what it does

SQLAlchemy is a Python SQL toolkit and ORM (Object Relational Mapper).

For this project, it lets us: - Configure connectivity to a database. -
Define Python classes that map to database tables. - Create and manage
sessions. - Perform database operations using Python objects and
methods.

An ORM maps between Python objects/classes and relational database
tables/rows.

### Engine: `create_engine()`

We import it:

```python
from sqlalchemy import create_engine
```

Then configure the database URL and engine:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./productivity.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
```

**Purpose of the engine**

The engine is SQLAlchemy's database connectivity infrastructure. It
knows how to connect to the configured database and manages the
underlying connections (including connection pooling where applicable).

It does **not** receive HTTP requests from clients. FastAPI handles HTTP
requests. A session uses the engine to communicate with the database.

Remember: - **Engine:** database connectivity infrastructure. -
**Session:** workspace/unit of work for database operations. -
**Database:** where the data is stored.

### Understanding the SQLite URL

```python
"sqlite:///./productivity.db"
```

  Part                Meaning

---

  `sqlite`            Database dialect/system
  `:///`              SQLite file-based URL form
  `./`                Current working directory
  `productivity.db`   Database filename

### Why `connect_args={"check_same_thread": False}`?

SQLite's default threading check restricts a connection to the thread
that created it. FastAPI applications can run synchronous
endpoint/dependency code in worker threads. This setting disables that
particular SQLite thread check for this setup.

It does not mean that arbitrary concurrent use of one session is safe. A
SQLAlchemy session should not be shared across concurrent requests or
threads; our design creates a session for each request.

---

## 5. Sessions and `sessionmaker()`

We import:

```python
from sqlalchemy.orm import sessionmaker
```

We configure a session factory:

```python
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False
)
```

### What is `sessionmaker`?

`sessionmaker()` creates a **factory** that can produce database
sessions.

`SessionLocal` is the factory, not an actual session.

When we call:

```python
db = SessionLocal()
```

we create an actual session object and store it in `db`.

### What does `bind=engine` mean?

It associates sessions created by this factory with our configured
engine. The sessions use that engine to communicate with the database.

### What does `autoflush=False` mean?

It disables SQLAlchemy's automatic flushing of pending changes before
queries. We will control the persistence flow explicitly in this
learning project.

### Session lifecycle

A session is used to perform database work. A simplified lifecycle is:

1. Create a session.
2. Perform database operations.
3. Commit changes if the transaction should be saved.
4. Close the session to release its resources.

Useful session methods:

---

  Method                              Purpose

---

  `db.add(object)`                    Adds an ORM object to the session;
                                      it is pending, not yet committed

  `db.commit()`                       Commits the current transaction

  `db.refresh(object)`                Reloads the object's values from
                                      the database

  `db.close()`                        Closes the session and releases its
                                      resources

`db.rollback()`                     Rolls back the current transaction
-------------------------------------------------------

**Important:** `db.add()` by itself does not permanently save a row.
`db.commit()` commits the transaction.

---

## 6. `declarative_base()` and `Base`

In `database.py` we added:

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

`declarative_base()` creates a base class for our SQLAlchemy declarative
models.

Our model classes inherit from `Base`. SQLAlchemy uses those model
definitions to build metadata describing the tables and columns.

`Base.metadata` is the collection of table metadata associated with that
base.

### Why do we import `models` before `create_all()`?

We use:

```python
from database import engine, Base
import models

Base.metadata.create_all(bind=engine)
```

Importing `models` executes the class definition for `Task`. That
registers the table definition with `Base.metadata`.

Then `create_all()` can see the registered table.

If the model module has not been imported, its table may not yet be
registered with that `Base`, so `create_all()` will not know to create
it.

### What does `create_all()` do?

```python
Base.metadata.create_all(bind=engine)
```

- Looks at the tables registered in `Base.metadata`.
- Checks the database for those tables.
- Creates tables that do not exist.

It does not automatically update an existing table's structure when you
change a model. Schema changes in a real evolving application are
normally managed with migrations (for example, Alembic).

---

## 7. SQLAlchemy model vs Pydantic schema

This distinction is essential.

### Pydantic schema

Example in `schemas.py`:

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskResponse(TaskCreate):
    id: int
```

Purpose: - Defines and validates API input. - Defines the shape of API
output. - Helps FastAPI document request and response bodies.

### SQLAlchemy model

Example in `models.py`:

```python
from sqlalchemy import Column, Integer, String
from database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
```

Purpose: - Defines how a database table is represented. - Defines the
table name and its columns. - Maps Python objects to rows in the
database.

### 			Compare them

  Pydantic schema                            			 SQLAlchemy model

---

  `TaskCreate`                               				 `Task`
  API data validation/serialization          			 Database table mapping
  `BaseModel` inheritance                     			 SQLAlchemy `Base` inheritance
  Used by FastAPI request/response handling  	 Used by SQLAlchemy ORM

We use `TaskCreate` for incoming data and `Task` for the database
object. Their names are deliberately different to avoid confusion.

---

## 8. Defining the `tasks` table

Our SQLAlchemy model:

```python
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
```

Breakdown:

---

  Code                                Meaning

---

  `class Task(Base)`                  Declares an ORM model using our
                                      declarative base

  `__tablename__ = "tasks"`           Maps this class to a table named
                                      `tasks`

  `Column(Integer, ...)`              Declares an integer column

  `primary_key=True`                  Makes `id` the primary key

  `index=True`                        Requests an index on the `id`
                                      column

  `nullable=False`                    The column cannot be NULL

`nullable=True`                     The column may contain NULL
------------------------------------------------

A primary key uniquely identifies a row in the table. In our model,
SQLite/SQLAlchemy will generate an integer primary key when a new task
is inserted without an explicit ID.

---

## 9. Dependency injection and `yield`

In `database.py`, we added:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

This is a FastAPI dependency that provides a database session to an
endpoint and ensures cleanup.

### What does `yield` do?

In a Python generator function, `yield`: 1. Produces a value. 2. Pauses
the function at that point. 3. Allows the function to resume later.

FastAPI supports dependencies that use `yield`. It runs the setup code
before `yield`, supplies the yielded value to the endpoint, and then
runs the cleanup code after the endpoint's work is finished.

In our function: - `db = SessionLocal()` creates a session. - `yield db`
provides that session to the endpoint. - `finally: db.close()` closes
the session during cleanup, including when the endpoint raises an
exception.

### `return` vs `yield`

```python
def get_value():
    return 10
```

`return` gives back a value and finishes the function.

```python
def get_value():
    yield 10
```

`yield` gives back a value and pauses the generator. It can resume
later.

In our FastAPI dependency, this pause/resume behaviour lets FastAPI
manage the session's lifetime around the request.

### What is dependency injection?

Dependency injection means a component receives something it needs from
an external provider instead of creating it itself.

Our endpoint declares:

```python
db: Session = Depends(get_db)
```

- `Depends(get_db)` tells FastAPI to call `get_db`.
- `get_db` yields a session.
- FastAPI supplies that session as the `db` argument.
- After request handling, FastAPI completes the dependency cleanup.

This gives each request its own session rather than keeping one global
session open for the whole application.

---

## 10. Our first database-backed POST endpoint

The final working endpoint in `main.py`:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Task
from schemas import TaskCreate, TaskResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return "Hello how are you!!"


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    new_task = Task(
        title=task.title,
        description=task.description
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task
```

### Walk through the request

A client sends:

```http
POST /tasks
```

with JSON:

```json
{
  "title": "Learn SQLAlchemy",
  "description": "Understand database integration with FastAPI"
}
```

The request flows through the following steps:

1. **FastAPI validates the body.** `TaskCreate` checks the incoming
   data.
2. **FastAPI provides a session.** `Depends(get_db)` runs the
   dependency and supplies `db`.
3. **Create an ORM object.** `Task(...)` constructs a Python object
   mapped to the `tasks` table.
4. **Add it to the session.** `db.add(new_task)` marks it as pending in
   the session.
5. **Commit.** `db.commit()` commits the transaction so the inserted
   row is saved.
6. **Refresh.** `db.refresh(new_task)` reloads database-generated
   values, including the generated `id`.
7. **Return the object.** FastAPI serializes it according to
   `TaskResponse`.
8. **Clean up.** The dependency resumes and calls `db.close()`.

### Why do we use `db.refresh()`?

The database generates the primary key for our new row. Refreshing the
object retrieves the generated value so it is available when we return
the response.

### Why `status_code=201`?

HTTP `201 Created` is the conventional success status for a request that
creates a new resource.

### Why `response_model=TaskResponse`?

Our database object has an `id`, `title`, and `description`.
`TaskResponse` describes that response shape and lets FastAPI validate
and serialize it.

---

## 11. Final file structure

At this stage, the project is organised like this:

```text
Productivity-tracker-backend/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── productivity.db
└── .venv/
```

### `database.py`

Responsibilities: - Configure the database URL. - Create the engine. -
Create the session factory. - Define the declarative `Base`. - Provide
`get_db()` for request-scoped sessions.

### `models.py`

Responsibilities: - Define SQLAlchemy ORM models. - Describe database
tables and columns.

### `schemas.py`

Responsibilities: - Define Pydantic request and response schemas.

### `main.py`

Responsibilities: - Create the FastAPI application. - Register routes. -
Make model metadata available and create missing tables. - Implement
endpoint logic.

---

## 12. How we tested it

We ran the application using:

```bash
fastapi dev main.py
```

Then opened:

```text
http://127.0.0.1:8000/docs
```

Swagger UI lets us inspect and call our API endpoints.

We tested `POST /tasks` with:

```json
{
  "title": "Learn SQLAlchemy",
  "description": "Understand database integration with FastAPI"
}
```

The task was successfully stored in the SQLite database file, and the
user confirmed that the record was visible in the database.

---

# Revision Questions

Try answering these without looking at the notes first. The questions
follow the concepts we discussed during implementation.

## A. FastAPI and schemas

1. What is the purpose of `app = FastAPI()`?
2. What does `@app.post("/tasks")` do?
3. What is an API endpoint?
4. What happens when an endpoint declares `task: TaskCreate`?
5. What is the difference between a Pydantic schema and a SQLAlchemy
   model?
6. What does `model_dump()` do?
7. Why do we use `response_model`?

## B. Engine and sessions

8. Why do we need `create_engine()`?
9. Does the engine receive HTTP requests from the client?
10. What is the difference between an engine and a session?
11. What does `sessionmaker()` create?
12. Is `SessionLocal` an actual session or a session factory?
13. What does `bind=engine` do?
14. What is the purpose of `autoflush=False`?
15. What does `db.add()` do?
16. Why isn't `db.add()` alone enough to commit a new row?
17. What does `db.commit()` do?
18. Why do we call `db.refresh()` after inserting a row?
19. What does `db.close()` do?

## C. Models and tables

20. What does `declarative_base()` create?
21. What is `Base`?
22. What is `Base.metadata`?
23. Why must we import `models` before calling
    `Base.metadata.create_all()`?
24. What does `create_all()` do?
25. Does `create_all()` automatically migrate an existing table when a
    model changes?
26. What does `__tablename__` specify?
27. What is a primary key?
28. What is the difference between `nullable=True` and `nullable=False`?
29. What is the purpose of `index=True`?

## D. Dependencies and `yield`

30. What is dependency injection?
31. What does `Depends(get_db)` tell FastAPI?
32. What is the purpose of `get_db()`?
33. What does `yield db` provide to the endpoint?
34. What is the difference between `return` and `yield`?
35. Why do we use `try/finally` around the yielded session?
36. What happens after the endpoint finishes using the session?

## E. Trace the POST endpoint

37. Why do we construct `Task(...)` instead of `TaskCreate(...)` for
    database insertion?
38. What happens when `db.add(new_task)` executes?
39. At what point is the transaction committed?
40. Why do we refresh the object?
41. Why does the endpoint return `new_task`?
42. Why did we use HTTP status code `201`?

---

# Answer Key

Try the questions before reading this section.

1. Creates the FastAPI application instance.
2. Registers a handler for POST requests at `/tasks`.
3. An API operation exposed through an HTTP method and path.
4. FastAPI parses and validates the request body using that Pydantic
   schema.
5. A schema validates API data; an ORM model maps Python objects to
   database tables.
6. Converts a Pydantic model instance into a Python dictionary.
7. To validate, serialize, and document the outgoing response shape.
8. To configure SQLAlchemy's database connectivity infrastructure.
9. No. FastAPI receives HTTP requests; the engine provides database
   connectivity.
10. The engine manages connectivity; a session manages a unit of
    database work.
11. A factory for creating sessions.
12. A factory.
13. Associates sessions from the factory with the configured engine.
14. Disables automatic flushing of pending changes before queries.
15. Adds an ORM object to the session as pending.
16. Because the transaction still needs to be committed.
17. Commits the current transaction.
18. To reload database-generated values, such as the new primary key.
19. Closes the session and releases its resources.
20. A declarative base class for ORM models.
21. The base class our ORM models inherit from.
22. Metadata describing tables registered with that base.
23. Importing the module executes model definitions and registers their
    tables.
24. Creates registered tables that do not already exist.
25. No. Existing schema changes need migrations.
26. The database table name.
27. A column (or set of columns) that uniquely identifies each row.
28. Whether a column can contain SQL NULL.
29. To create an index that can help database lookups.
30. Supplying a component with something it needs from an external
    provider.
31. To execute the dependency and provide its yielded value to the
    endpoint.
32. To create and provide a session, then clean it up.
33. The session object.
34. `return` finishes the function; `yield` produces a value and pauses
    a generator that can resume later.
35. To ensure cleanup happens even if an exception occurs.
36. FastAPI resumes the dependency and executes `db.close()`.
37. `Task` is the SQLAlchemy model mapped to the table; `TaskCreate` is
    only the input schema.
38. The object becomes pending in the session.
39. At `db.commit()`.
40. To retrieve generated database values, such as the primary key.
41. FastAPI uses the returned ORM object to build the response.
42. `201 Created` indicates successful resource creation.

---

# What we have completed

- [X] Created a FastAPI application.
- [X] Implemented basic in-memory CRUD.
- [X] Understood Pydantic request and response schemas.
- [X] Installed SQLAlchemy.
- [X] Configured a SQLite engine.
- [X] Created a session factory.
- [X] Defined the SQLAlchemy declarative base.
- [X] Created a SQLAlchemy Task model.
- [X] Created the database table using `Base.metadata.create_all()`.
- [X] Implemented a session dependency using `yield`.
- [X] Implemented a database-backed `POST /tasks`.
- [X] Verified that the created task is stored in SQLite.

## Next implementation milestone

The next logical step is to implement database-backed retrieval:

- `GET /tasks` --- retrieve all tasks.
- `GET /tasks/{task_id}` --- retrieve one task.
- Handle missing IDs with HTTP 404.

After that, we'll replace the old in-memory update and delete operations
with database operations too.

**Revision tip:** Focus especially on the distinction between engine,
session factory, session, ORM model, and Pydantic schema. Those are the
core concepts we've introduced so far.
