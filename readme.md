# Lab 2 — DFS password puzzle

## 1. Overview

Both frontend and backend code are already implemented. You do **not** write code for this lab.

Your task instead: Discover your login password from `backend/puzzle.json`, then use the provided
login UI to see if you can login with your student ID and password.

## 2. File structure

```
Lab2/
├── frontend/               # login UI + file list (provided)
├── backend/
│   ├── auth_crypto.py
│   ├── data_logic.py
│   ├── rest_service.py     # REST on :8000
│   ├── puzzle.json         # solve this for your password
│   └── users.xml           # stored credentials (provided)
├── data/                   # sample files (main.py, utils.js)
├── requirements.txt
└── readme.md
```

## 3. Setup and run

From `Lab2/`:

```bash
pip install -r requirements.txt
```

Two terminals:

```bash
python3 backend/rest_service.py
python3 frontend/serve.py
```

Open http://127.0.0.1:5500/

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5500/ |
| REST docs | http://127.0.0.1:8000/docs |

## 4. What is the password?

`backend/puzzle.json` is a nested JSON tree of lists, dicts, and length-1 strings
(dict keys are also length-1).

**Password definition:** take a depth-first walk of the tree. Along the walk you
collect (1) path **indices** and (2) a digit string from digit characters you
meet (letter characters do **not** count toward that digit string). The first
time that digit string equals **your student id**, your password is the
combination of all indices on the path so far (joined with `-`).

NOTE: Letters may be ignored when matching the student id; they still sit on the path
and contribute their indices to the password.

How the server stores / checks passwords is left for you to read in the backend
(`auth_crypto.py`, `data_logic.py`, `rest_service.py`). 

We have provided an example ID and the password, with which you can enter the system:
```
"20784676": "4-6-6-7-8-2-7-3-1-9-6-8-7-6-9-3-3-7-5"
```

### 4.1 A simple example of the JSON format and password

```json
[
  {
    "a": ["n"],
    "2": {
      "0": {
        "b": {
          "7": {
            "8": {
              "c": {
                "4": {
                  "6": {
                    "7": {
                      "6": "z"
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
]
```

For student id **`20784676`**, letter keys `"b"`, and `"c"` appear on the
path. They do not change the digit string, but each still adds an index.
Because `"a"` comes first, `"2"` is at index `1`, so the password starts with `1`:

```text
1-0-0-0-0-0-0-0-0-0
```

Your real password comes from `backend/puzzle.json`, not from this example.

## 5. TODO

1. Setup the environment and run up the backend and frontend.
2. Solve `backend/puzzle.json` for the password that matches your student id.
3. Sign in with the password you found. If the login could succeed, you could submit your ID and password. 

## 6. Submission

To Canvas: Your ID and password.
