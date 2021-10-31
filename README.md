## Alarm Clock
Custom component adding phone-like recurring alarm clocks to the Home Assistant

### Features

* Multiple Alarms
* Weekday selector
* Ability to temporarily disable Alarms (e.g. vacation)
* Verbose state, see below

### Installation

Add this repo to the HACS as Integration

### State value

State sensor exposes the following values when alarm time is reached:

```
     -30m     -20m     -10m     0m       +10m     +20m     +30m
-----|--------|--------|--------|--------|--------|--------|-----
 off  minus_30 minus_20 minus_10    on    plus_10  plus_20   off
```

The value can be used in Automations to trigger the scenes, play music, etc.

### Screenshots