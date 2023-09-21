# Cribl Pack for Palo Alto Networks Firewalls
----

The Cribl Pack for Palo Alto Networks Firewalls processes events with the following goals in mind:
1. Events are received via syslog directly from Palo Alto firewalls
1. Add Splunk metadata to events (e.g. index, source, sourcetype, host)
2. Reduction of events by trimming the Syslog header and removing unnecessary fields such as "future_use" and "time" fields.

You should expect to see 15-30% reduction in the size of your Palo Alto Firewall log data.

## Installation
---
1. Install this pack from the [Cribl Pack Dispensary](https://packs.cribl.io), use the Git clone feature inside Cribl Stream, or download the most recent .crbl file from the repo [releases page](https://github.com/criblpacks/cribl-palo-alto-networks/releases).
2. Create a Route with a filter for your Palo Alto Firewall events. A sample filter to match all events:
```
(sourcetype=='pan:log' || sourcetype=='pan_log' || /^[^,]+,[^,]+,[^,]+,(THREAT|TRAFFIC|SYSTEM|CONFIG|HIPMATCH|CORRELATION|USERID|GLOBALPROTECT),/.test(_raw))
```
3. Select the `cribl-palo-alto-networks` pack as the pipeline.
4. Configure the Global Variable (`pan_default_index`) inside the Pack with the appropriate Splunk index for your Palo Alto logs. By default, the index field will be set to `pan_logs`.

### Configure Device Information
This pack assumes all of your firewalls use UTC/GMT for their time zone configuration. If you use local time zones, please configure the `device_info.csv` lookup file (located in the pack's Knowledge content).

The `device_info.csv` file uses a regular expression lookup function in each pipeline. You can use wildcards (e.g. `.*`, `KCMO-FW-\d+`, `FW-.*`) in the hostname field. The time zone (`tz`) field must be formatted as an integer (e.g. -05, +11, etc.). The regex lookup will return the most specific regex as the time zone value.

Here is an example lookup file:
```
host,tz
KCMO-FW-\d+,America/Chicago
FW-.*,Etc/GMT+1
.*,US/Eastern
```

## Release Notes
---
### Version 1.1.2 - 2023-09-21
* Fix issue with time zone function in Correlation pipeline

### Version 1.1.1 - 2023-03-14
* Fixes typo in Correlation pipeline

### Version 1.1.0 - 2022-04-12
* Fixes incorrect sourcetype set in Decryption pipeline
* Add explanations why fields are dropped
* New feature: use Global Variables to define default `index` and `source` field values. Change in one location instead of every pipeline!
* Rewrites pipeline logic to separate parser reserialize function into separate parser extract and serialize functions
* New feature: set the global variable `pan_device_name_as_host` to use set the `host` field value from the `dvc_host` field value instead of the syslog header.

### Version 1.0.0 - 2022-03-22
* Update to version 1.0.0 - major release for new Pack Dispensary 🎉
* Changes Pack ID from `PAN` to `cribl-palo-alto-networks` to match naming convention of Cribl built Packs.
* This is a **breaking** change and all references in Routes/Pipelines must be updated!

### Version 0.7.0 - 2022-03-10
* Updates parser fields to PAN OS 10.2. All fields added in PAN OS 10 are removed from events by default.

### Version 0.6.3 - 2022-03-03
* Adds Correlation event log pipeline.

### Version 0.6.2 - 2021-11-17
* `device_info.csv` now uses Olson formatted timezones (e.g. `America/Chicago`) instead of static offsets and the [`C.Time.adjustTZ`](https://docs.cribl.io/logstream/cribl-reference/#time) function for better time zone support. A listing of time zones can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List).

### Version 0.6.1 - 2021-11-02
* Bug fix - Corrects an issue in pipelines where the hostname is not correctly extracted if the date is a single digit. Unifies the hostname extraction across all pipelines.
* Routes use `indexOf` filter instead of `test` for higher performance. 

### Version 0.6.0 - 2021-09-14
* Adds `device_info.csv` lookup file and lookup function in pipelines to adjust time zones per firewall.

### Version 0.5.2 - 2021-08-12
* Adds pack display name for LogStream v3.1

### Version 0.5.1 - 2021-07-21
* Fixes README

### Version 0.5.0 - 2021-07-20
* Initial release


## Contributing to the Pack
---
Discuss this pack on our Community Slack channel [#packs](https://cribl-community.slack.com/archives/C021UP7ETM3).

## Contact
---
The author of this pack is Brendan Dalpe and can be contacted at <bdalpe@cribl.io>.

## License
---
This Pack uses the following license: [`Apache 2.0`](https://github.com/criblpacks/cribl-palo-alto-networks/blob/master/LICENSE).
