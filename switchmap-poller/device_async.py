async def device_async(poll_meta):
    # ... skip-file check ...
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, poll_device_sync, poll_meta)
    # result could be the processed data or None
