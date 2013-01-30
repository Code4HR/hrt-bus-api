To run script on Iron.io:

Upload
iron_worker upload process-gtfs

Schedule (Run once a day a noon [EST])
iron_worker schedule process-gtfs --start-at "2013-01-13T12:00:00-05:00" --run-every 86400