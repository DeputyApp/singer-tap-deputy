# Deputy + Stitch

## Connecting Deputy

Connecting Deputy to StitchData is as simple as addping Deputy as a data source for Stitch.

- Sign into your Stitch account.
- On the Stitch Dashboard page, click the Add Integration button.
- Click the Deputy icon.
- Enter a name for the integration. This is the name that will display on the Stitch Dashboard for the integration; it’ll also be used to create the schema in your destination.

For example, the name “Stitch Deputy” would create a schema called stitch_deputy in the destination. Note: Schema names cannot be changed after you save the integration.

Click Save Integration.



### Requirements

To set up Deputy in Stitch, you need:

- Active Deputy account
- Administrative login to Deputy. Please note if this login (or user) is ever discarded or changed access level, then the data sync will stop working!

#
## [tap_name] Replication

If pertinent, include details about how the tap replicates data and/or uses the API. As Stitch users are billed for total rows replicated, any info that can shed light on the number of rows replicated or reduce usage is considered necessary.

Examples:

- Replication strategy - attribution/conversion windows ([Google AdWords](https://www.stitchdata.com/docs/integrations/saas/google-adwords#data-extraction-conversion-window)), event-based updates, etc.
- API usage, especially for services that enforce rate limits or quotas, like Salesforce or [Marketo](https://www.stitchdata.com/docs/integrations/saas/marketo#marketo-daily-api-call-limits)

---

## [tap_name] Table Schemas

For **each** table that the tap produces, provide the following:

- Table name: 
- Description:
- Primary key column(s): 
- Replicated fully or incrementally _(uses a bookmark to maintain state)_:
- Bookmark column(s): _(if replicated incrementally)_ 
- Link to API endpoint documentation:

---

## Troubleshooting / Other Important Info

Anything else users should know about using this tap? For example: `some_column` is a Unix timestamp.
