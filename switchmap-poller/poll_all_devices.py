async def poll_all_devices():
    config = ConfigPoller()
    hosts = [_META(zone=zone.name, hostname=h, config=config) 
             for zone in sorted(config.zones()) for h in zone.hostnames]
    # Here I Launch tasks for each device
    tasks = [asyncio.create_task(device_async(meta)) for meta in hosts]
    await asyncio.gather(*tasks)  # waiting for all devies to finish
