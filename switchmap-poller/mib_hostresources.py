class HostResourcesQuery(Query):
    def cpu_load(self):
        oid = "1.3.6.1.2.1.25.3.3.1.2"  # hrProcessorLoad
        results = self.snmp_object.walk(oid, normalized=True)
        loads = [int(v) for v in results.values()]
        if loads:
            return sum(loads) / len(loads)  # average CPU %
        return None
