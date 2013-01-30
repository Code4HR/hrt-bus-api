To run script on Iron.io:

Upload
iron_worker upload process-ftp

Schedule (Run once a minute for no longer than 10 seconds)
iron_worker schedule process-ftp --run-every 60 --timeout 10