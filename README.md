# motion-analysis

master's thesis project, assessments of POEs in videos.
report: [Visual assessments of Postural Orientation Errors using ensembles of Deep Neural Networks](https://github.com/filipkro/motion-analysis/blob/master/tex/mt-motion-analysis.pdf)

This repo contains backend for mobile application. 

Run with `docker-compose`:
```
docker compose build
```
to build image, and
```
docker compose up
```
to run backend, `inference/test-flask/req.py` contains some (very messy) code to call the API.
