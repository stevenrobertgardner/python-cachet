#!/usr/bin/env python3

# expedient and bad functional test, using local docker cachet.

import cachet
conn = cachet.Connection('http://192.168.99.100:8019','TWzGvm2X9MRVJ1TfeBPG')
print(conn.health())
print(conn.version())
print("get_components()")
print(conn.get_components())
print("get_component(1)")
print(conn.get_component(1))
print("get_component_groups()")
print(conn.get_component_groups())
print("get_component_group(1)")
print(conn.get_component_group(1))
print("get_incidents()")
print(conn.get_incidents())
print("get_incident(1)")
print(conn.get_incident(1))
print("get_metrics()")
print(conn.get_metrics())
print("get_metric(1)")
print(conn.get_metric(1))
print("get_subscribers())")
print(conn.get_subscribers())
