# Scripts

Both scripts require setting the following environment variables:

* `db_uri`
* `db_name`

## GTFS

`python gtfs.py [daysRelativeToToday]`

Downloads GTFS data and loads one day's schedule into the database. Realtime data from HRT is relative to schedule data, so this data is necessary to correct interpret realtime data.

If `daysRelativeToToday` is not specified, it defaults to `1`, which means that the schedule for the following day is loaded. To load the current day's data, run `python gtfs.py 0`.

## FTP

`python ftp.py`

Downloads realtime data from HRT, matches to scheduled data and stores results in database.

# Deployment

The scripts can be deployed to AWS Lambda using [Serverless](https://serverless.com) where they will run periodically.

Set environment variables in `serverless.yml`

Note that HRT's FTP server only allows whitelisted IPs, so you'll need to set up a VPC. [Here is one guide on how to do that](http://techblog.financialengines.com/2016/09/26/aws-lambdas-with-a-static-outgoing-ip/).

Install Serverless  
`npm install -g serverless`

Install python requirements plugin  
`npm install --save serverless-python-requirements`

Configure AWS credentials

Create and activate a virtual environment  
```
virtualenv venv
source venv/bin/activate
```

Deploy  
`serverless deploy -v`
