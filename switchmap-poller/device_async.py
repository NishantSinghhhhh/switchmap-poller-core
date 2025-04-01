async def device_async(poll_meta):
    # ... skip-file check ...
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, poll_device_sync, poll_meta)
    # result could be the processed data or None

# Here, poll_device_sync is a regular function that encapsulates the 
# original steps for polling one device (essentially the body of the old device() function):
# python
# Copy

def poll_device_sync(poll):
    hostname, zone, config = poll.hostname, poll.zone, poll.config
    # Create Poll object and query SNMP data (synchronous)
    poller_obj = poller.Poll(hostname)      # may perform SNMP credential validation
    snmp_data = poller_obj.query()          # blocking call to gather SNMP data
    if snmp_data and isinstance(snmp_data, dict):
        data = udevice.Device(snmp_data).process()  # process raw SNMP data into structured form
        data["misc"]["zone"] = zone
        # Post data to API server (HTTP) or print, depending on 'post' flag
        rest.post(API_POLLER_POST_URI, data, config)
        return data
    else:
        log_message = f"Device {hostname} returns no data. Check connectivity and/or SNMP configuration"
        log.log2debug(1025, log_message)  # same logging as before
        return None
