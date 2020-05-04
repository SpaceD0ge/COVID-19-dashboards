# Tools for the COVID-19 information processing.
Simple model evaluation dashboard.

## Requirements

python 3.5+

internet access

## Getting started

```python
prediction_files = glob('./submissions/*.csv')
team_names = [x.split('/')[-1][:-4] for x in prediction_files]

start_date = "2020-04-27"
end_date = "2020-05-03"
```
Change this code in the app.py file to process your own predictions.

## Serving

[Follow this tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)