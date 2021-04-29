# election-tools
scripts for simplifying the process of matching NYS and NYC election data to geographical data

This is a simple module that you can use for loading and reshaping election results at the ED level found on the NYC Board of Elections website.

Newer election results (2018 and newer) tend to have these weird butchered tables. This module can clean these tables up. By using `election_tools.fix_election_file(fname_in, fname_out)`, you can fix these election results, with the file being written to fname_out.

You can also load these cleaned election results as a pandas dataframe by using `election_tools.load_election(fname_in)`.

Both of these functions have an option called candidates_as_columns, which is set to False as default. If you set it to true, the result will have candidate names as columns, with ED-level Tallies in the rows. Additionally, the column elect_dist provided gives ED-labels in a format consistent with those found in ED shapefiles on NYC Open Data.
