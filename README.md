# Cribl Pack for Palo Alto Networks Firewalls
----

The Cribl Pack for Palo Alto Networks Firewalls processes events with the following goals in mind:
1. Events are received via syslog directly from Palo Alto firewalls
1. Add Splunk metadata to events (e.g. index, source, sourcetype, host)
2. Reduction of events by trimming the Syslog header and removing unnecessary fields such as "future_use" and "time" fields.

You should expect to see 15-30% reduction in the size of your Palo Alto Firewall log data.

## Installation
---
1. Download the most recent .crbl file from the repo [releases page](https://github.com/criblpacks/cribl-palo-alto-networks/releases).
2. Create a Route with with a filter for your Palo Alto Firewall events. A sample filter to match all events:
```
(sourcetype=='pan:log' || sourcetype=='pan_log' || /^[^,]+,[^,]+,[^,]+,(THREAT|TRAFFIC|SYSTEM|CONFIG|HIPMATCH|CORRELATION|USERID|GLOBALPROTECT),/.test(_raw))
```
3. Select the `PAN` pack as the pipeline.
4. Configure the pack pipelines with the appropriate index for your Palo Alto logs. By default the index field will be set to `pan_logs`.

## Release Notes
---
### Version 0.5.1 - 2021-07-21
Fixes README

### Version 0.5.0 - 2021-07-20
Initial release


## Contributing to the Pack
---
Discuss this pack on our Community Slack channel [#packs](https://cribl-community.slack.com/archives/C021UP7ETM3).

## Contact
---
The author of this pack is Brendan Dalpe and can be contacted at <bdalpe@cribl.io>.

## License
---
This Pack uses the following license: [`Apache 2.0`](https://github.com/criblio/appscope/blob/master/LICENSE).