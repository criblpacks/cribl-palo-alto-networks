# PAN Pack Flow Diagram

The following diagram shows illustrates the general process flow followed by the PAN Pack.

This pack is typically applied to a main route under Routing>Data Routes or as a Quick Connect Pack (in the case of a single data source).

The general route filter can be found on the [README page](README.md#installation).

Once inside the pack, each route filter picks only the subtype of log it will process. E.g. Traffic, Threat, etc.

Data is then forwarded to the output(s) configured by the main route or Quick Connect.

```mermaid
flowchart TD

subgraph pack[PAN Pack]
    direction LR
    traffic>Traffic]-->traffic_filter(["_raw.indexOf#40;,TRAFFIC,#41; > -1"])-->pan_traffic
    threat>Threat]-->threat_filter(["_raw.indexOf#40;,THREAT,#41; > -1"])-->pan_threat
    system>System]-->system_filter(["_raw.indexOf#40;,SYSTEM,#41; > -1"])-->pan_system
    config>Config]-->config_filter(["_raw.indexOf#40;,CONFIG,#41; > -1"])-->pan_config
    hip>HIP Match]-->hipmatch_filter(["_raw.indexOf#40;,HIPMATCH,#41; > -1"])-->pan_hipmatch
    uid>User ID]-->userid_filter(["_raw.indexOf#40;,USERID,#41; > -1"])-->pan_userid
    gp>GlobalProtect]-->gp_filter(["_raw.indexOf#40;,GLOBALPROTECT,#41; > -1"])-->pan_globalprotect
    decryption>Decryption]-->decrypt_filter(["_raw.indexOf#40;,DECRYPTION,#41; > -1"])-->pan_decryption
end

syslog{{Syslog source}}-->main_route>PAN Route]-->f;
f(["sourcetype=='pan:log' || sourcetype=='pan_log' || \n/^[^,]+,[^,]+,[^,]+,(THREAT|TRAFFIC|SYSTEM|CONFIG|HIPMATCH|CORRELATION|USERID|GLOBALPROTECT),/.test(_raw)"])-->pack;
pack-->output{{"Output#40;s#41;"}}
```