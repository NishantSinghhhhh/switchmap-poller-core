import asyncio
from switchmap.poller import poller, configuration
from switchmap.poller.update import device as udevice
from switchmap.core import rest, log, files
import os  # Make sure os is imported for file system checks

# Synchronous helper function to poll one device.
# I'm writing this function to handle the device polling in a blocking manner,
# and then offload it to an executor in the async flow.
def poll_device_sync(meta):
    # Extract device details from the meta object.
    hostname, zone, config = meta.hostname, meta.zone, meta.config

    # Check if a "skip" file exists, which tells us to bypass polling this device.
    skip_file = files.skip_file(poller.AGENT_POLLER, config)
    if os.path.isfile(skip_file):
        log.log2debug(1041, f"Skip file {skip_file} found. Skipping poll for {hostname} in zone \"{zone}\"")
        return None

    # Instantiate the Poll object to prepare SNMP polling.
    # This sets up SNMP and may validate credentials as needed.
    poll_obj = poller.Poll(hostname)
    
    # Query the device for SNMP data.
    # Note: This is a blocking call that may take time to complete.
    snmp_data = poll_obj.query()
    
    # Process and post the SNMP data if it is valid.
    if bool(snmp_data) and isinstance(snmp_data, dict):
        # Process the raw SNMP data into a structured format.
        data = udevice.Device(snmp_data).process()
        # I'm adding zone information to the processed data for context.
        data["misc"]["zone"] = zone
        # Post the processed data to the API. This is also a blocking operation.
        rest.post(poller.API_POLLER_POST_URI, data, config)
        return data
    else:
        # Log a debug message if no valid data is returned.
        log.log2debug(1025, f"Device {hostname} returns no data. Check connectivity and/or SNMP configuration")
        return None

# Asynchronous task to poll a device.
# This function wraps the synchronous polling in an executor to avoid blocking the event loop.
async def device_async(meta):
    loop = asyncio.get_running_loop()
    try:
        # Run the synchronous poll in a separate thread.
        await loop.run_in_executor(None, poll_device_sync, meta)
    except Exception as e:
        # Log an error if any exception occurs during polling.
        log.log2error(1001, f"Error polling {meta.hostname}: {e}")

# Main asynchronous routine to poll all devices.
# I use this function to collect all device metadata and then launch an async polling task for each device.
async def poll_all_devices():
    # Initialize configuration for the poller.
    config = configuration.ConfigPoller()
    metas = []
    
    # Build a list of metadata objects for each zone and its devices.
    for zone in sorted(config.zones()):
        for hostname in zone.hostnames:
            metas.append(poller._META(zone=zone.name, hostname=hostname, config=config))
    
    # Create a list of async tasks for all device polling operations.
    tasks = [asyncio.create_task(device_async(m)) for m in metas]
    
    # Await completion of all polling tasks.
    await asyncio.gather(*tasks)
