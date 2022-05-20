# Concord API
Opinionated, blazingly-fast backend API for Concord.

# Stack

- [Uvicorn](https://uvicorn.org)
- [Blacksheep](https://github.com/Neoteroi/BlackSheep)
- [Cassandra](https://cassandra.apache.org)

# Abuse Protection
Ekranoplan has been made to allow as little abuse of the API as possible
and use as little database calls as needed.
To try and avoid DDoS Attacks we recommend using [cloudflare](https://cloudflare.com).

# Running

- Prerequisites
    - A Cassandra Database
    - A Redis Database

    Please run `ekranoplan/database.py` to setup the 
    cassandra or scylla database (make sure to have the "airbus" keyspace available).
    The redis database does not need any prior setup.

    If your db host has a ssl bundle, please set `safe=true` in your `.env` 
    and add the bundle as `bundle.zip` in `ekranoplan/static`.

- Development
    
    Running `run.py` should be fine.

- Production
    
    When you deploy in production we recommend:
    
    - Using Kubernetes
