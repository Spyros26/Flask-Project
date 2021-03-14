# Flask Web App Project for NTUA Software Engineering Class
# EV Charging System
#### by: Georgoutsos Athanasios, Dragazis Spyridon, Valouxis Spyridon

## Main Use-Cases

1. Charging EV

2. Issue Statement (statement with all the charging sessions in a selected period)

## User Roles

1. Admin (default admin account has username: admin and password: petrol4ever)

2. Privileged (role for privileged stakeholders who can access SessionsPerXX endpoints from cli)

3. User (role for typical EVUsers)

## Setup & Installtion

Make sure you have the latest version of Python installed.

```bash
git clone <repo-url>
```

```bash
pip install -r requirements.txt
```

## Running The App

```bash
python main.py
```

## Viewing The App

Go to http://localhost:8765/evcharge/api/
