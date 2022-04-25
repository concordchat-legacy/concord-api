# Ekranoplan
Privacy-focused, scalable, and blazingly fast REST API for concord.

# Design Philosophy
You may be asking multiple questions, like "why is this in python?" or "why not use rust?"
Answers to those exact questions are stated, [here]


# Abuse Protection
Ekranoplan has been made to allow as little abuse of the API as possible
and use as little database calls as needed.
to try and avoid DDOS Attacks we recommend using [cloudflare](https://cloudflare.com).

# Running

- Prerequisites
    - A Cassandra Database
    - A Redis Database

    Please run `ekranoplan/database.py` to setup the 
    cassandra database or scylla(make sure to have the "ekranoplan" keyspace available).
    The redis database does not need any prior setup.

    If your cassandra host has a db bundle please set `safe=true` in your `.env` 
    and add the bundle as `bundle.zip` in `ekranoplan/static`.

- Development
    
    Running `run.py` should be fine.

- Production
    
    When you deploy in production we recommend:
    
    - Using Kubernetes or Docker
    - Running `run.py` only

# Stack

- [Python](https://python.org)
- [Blacksheep](https://github.com/Neoteroi/BlackSheep)
- [Uvicorn](https://uvicorn.org)
- [snowflake.py](https://pypi.org/project/snowflake.py)
- [uvloop](https://github.com/MagicStack/uvloop)
- [and more](https://github.com/cncrd/ekranoplan/blob/master/requirements.txt)
