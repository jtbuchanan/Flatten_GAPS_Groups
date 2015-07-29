Flatten\_GAPS\_Groups
======================

Python script to flatten nested Google Apps Groups. This leverages the Google Apps Admin SDK. 

Why would I need this?
-----

Unfortunately, some extensions built for Google Apps domains do not support querying group users contained in groups that are nested under a parent.

This script simply takes all of the users associated to a group, be them the users assigned at the parent level or the users assigned to a nested group, and ensures the users are a member of the parent group. 

Usage
-----

Most likely, you will not want all of your GAPS groups to be flattened. This script will only flatten the groups where the name of the group starts with a prefix that you specify in the script. 

Note: The groups that will be flattened have the prefix matched to their "Name" not their e-mail address. 

1. Change the 'prefix' variable at the top of the script to the appropriate string for your needs
2. Run the script:
	
	python flatten_gaps_groups.py
