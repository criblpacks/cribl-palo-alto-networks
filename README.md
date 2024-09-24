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
This pack assumes firewalls currently use UTC/GMT for their time zone configuration. If any device uses a local time zone, please configure an entry in the `device_info.csv` lookup file (located in the pack's Knowledge content) to adjust timestamps with the timezone of the firewall. The timezone acts as the offset to adjust the timestamp of the event to UTC with the [Auto Timestamp function](https://docs.cribl.io/stream/auto-timestamp-function/).

The lookup file expects data in two columns: `host` and `tz`.

#### Host

The `host` field accepts a regular expression to match the hostname of the firewall. The most specific regex in the lookup will be used to match the timezone.

Consider an example with the following hostnames using a standard naming convention. The format follows this pattern:
* Static `FW` string
* ISO 3166-1 alpha-2 country code
* Optional State or Province code
* City or IATA airport code
* Device identifier

Here are some example hostnames:
* `FW-US-MO-KC-01`
* `FW-US-MO-KC-02`
* `FW-US-MO-STL-01`
* `FW-US-TX-DFW-01`
* `FW-US-TX-AUS-01`
* `FW-US-TX-ELP-01`
* `FW-UK-LON-01`
* `FW-JP-HND-01`

The first 5 examples are in the US Central time zone. El Paso, Texas (ELP) observes Mountain Time. The final two examples are London and Tokyo, in the Europe/London and Asia/Tokyo time zones, respectively.

A regex of `FW-\d+` would match all firewalls, and a specific regex of `FW-US-MO-KC-\d+` would only match the firewalls in the Kansas City data center. Matches for `FW-US-MO-KC\d+` will take higher precedence over the `FW-\d+` regex. This functionality can be used to match specific firewalls or groups of firewalls and provide a timezone for each with increasing precedence. More information about this behavior is provided on the [Cribl Documentation Lookup Function page](https://docs.cribl.io/stream/lookup-function/#usage).

#### Timezone Configuration

Time zones are configured using Olson formatted timezones (e.g. `America/Chicago`) [`C.Time.adjustTZ`](https://docs.cribl.io/logstream/cribl-reference/#time). A listing of time zones can be found [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List).

Cribl uses a third-party library, [`timezone-support`](https://www.npmjs.com/package/timezone-support), to import timezone definitions. As of the time of writing, Cribl uses [version 2.0.2](https://github.com/prantlf/timezone-support/releases/tag/v2.0.2) of this package which supports all time zones up to the 2019a release of the IANA Time Zone Database, but may include more up-to-date entries. Please verify before using a specific timezone. All changes to the timezone database since 2016 can be found [here](https://tzdata-meta.timtimeonline.com/).

#### Example Lookup File

Here is an example lookup file based on the scenario above utilizing increasing regex specificity for timezone matching:
```
host,tz
FW-US-.*,America/Chicago
FW-US-TX-ELP-.*,America/Denver
FW-JP-.*,Asia/Tokyo
FW-UK-.*,Europe/London
```

Firewalls not matching any entry in this list would be assumed to currently have timestamps in UTC.

## Release Notes
---
### Version 1.1.5 - 2024-09-24
* In pan_traffic pipeline, add missing `src_dvc_profile` field to the serializer function

### Version 1.1.4 - 2024-07-02
* In pan_threat pipeline, remove two fields from list of fields to be dropped, "src_location" & "dest_location"

### Version 1.1.3 - 2024-07-02
* Fix various typos in pipelines.

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
