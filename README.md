# Ekranoplan
Privacy-focused, scalable, and blazingly fast REST API for concord.

# Stack

- [Uvicorn](https://uvicorn.org)
- [Blacksheep](https://github.com/Neoteroi/BlackSheep)
- [Cassandra](https://cassandra.apache.org)

# Design Philosophy
You may be asking multiple questions, like "why is this in python?" or "why not use rust?"
Answers to those exact questions are stated, [here]


# Abuse Protection
Ekranoplan has been made to allow as little abuse of the API as possible
and use as little database calls as needed.
To try and avoid DDoS Attacks we recommend using [cloudflare](https://cloudflare.com).

# Running

- Prerequisites
    - A Cassandra Database
    - A Redis Database
    - A Amazon S3 Bucket named `cdn.concord.chat`

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
