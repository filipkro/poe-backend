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


Specify filepath for mounting in `docker-compose.yml`. The endpoint to call to analyse a video is `/analyse_video`, this is a POST request where the filepath (`path`) from the mount point to the video should be specified as well as for which leg (`leg`) the motion is performed (R or L). For the example data provided the following data should be passed in the request

```
{'path': 'vid.mp4', 'leg': 'R'}
```
