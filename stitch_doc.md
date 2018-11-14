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
## Deputy Replication

Your selected [Deputy resources](https://www.deputy.com/api-doc/Resources/Employee) will be synchorized by [Resource API calls](https://www.deputy.com/api-doc/API/Resource_Calls). All tables as "id" as primary key and "modified" as timestamp that is used to finding new/updated data since last sync. 

