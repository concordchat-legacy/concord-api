#!/bin/bash
docker build -t concore .
docker run -d -p 5000:5000 concore
