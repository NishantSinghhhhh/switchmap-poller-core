def devices(multiprocessing=False):
    """Poll all devices for data using subprocesses and create YAML files."""
    arguments, batched_data = [], []
    config = ConfigPoller()
    pool_size = config.agent_subprocesses()
    zones = sorted(config.zones())

    for zone in zones:
        arguments.extend(
            _META(zone=zone.name, hostname=_, config=config) for _ in zone.hostnames)

    if not multiprocessing:
        for argument in arguments:
            data = device(argument, post=False)
            if data:
                batched_data.append(data)
                if len(batched_data) >= pool_size:
                    rest.post(API_POLLER_POST_URI, batched_data, config)
                    batched_data.clear()
    else:
        with Pool(processes=pool_size) as pool:
            results = pool.map(device_wrapper, arguments)
        batched_data.extend(filter(None, results))
    if batched_data:
        rest.post(API_POLLER_POST_URI, batched_data, config)
