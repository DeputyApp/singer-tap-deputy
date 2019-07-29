# tap-deputy

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [Deputy's API](https://www.deputy.com/api-doc/API/Getting_Started)
- Extracts from all [resources](https://www.deputy.com/api-doc/Resources)
- Outputs the schema for each resource

## Configuration

Take a look at the [example config](example.config.json) as a starting point for creating your own.

THe tap requires an OAuth client is configured and a refresh token is issued. Follow the Deputy [authentication docs to setup an OAuth client](https://www.deputy.com/api-doc/API/Authentication).

Config properties:

| Property | Required | Example | Description |
| -------- | -------- | ------- | ----------- |
| `domain` | Y | "usdemo.ent-na.deputy.com" | The domain the Deputy account runs on. |
| `client_id` | Y | | The Deputy OAuth client ID |
| `client_secret` | Y | | The Deputy OAuth client secret |
| `redirect_uri` | Y | "http://localhost:500/callback" | The Deputy OAuth client redirect URI |
| `start_date` | Y | "2010-01-01T00:00:00Z" | The default start date to use for date modified replication, when available. |
| `user_agent` | N | "Vandelay Industries ETL Runner" | The user agent to send on every request. |


## Usage

First read through Singer's [Running and Developing Singer Taps and Targets](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-and-developing-singer-taps-and-targets) for getting started with running a tap and target.

For basic usage, run `tap-deputy` with the configuration file.

Discovery:

```sh
tap-deputy -c my-config.json --discover
```

Sync:

```sh
tap-deputy -c my-config.json --catalog my-catalog.json
```

---

Copyright &copy; 2019 Stitch
