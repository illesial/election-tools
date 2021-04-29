import pandas as pd
import geopandas as gpd
import shapely
from functools import reduce
pd.options.mode.chained_assignment = None

def load_election_df(fname):
    colnums=[i + 11 for i in range(11)]
    colnames = ['AD', 'ED', 'County', 'EDAD Status', 'Event', 'Party/Independent Body', 'Office/Position Title', 'District Key', 'VoteFor', 'Unit Name', 'Tally']
    colmapper = dict(zip(colnums, colnames))
    df = pd.read_csv(fname, header=None)
    if len(df.columns) == 22:
        df = df[colnums].rename(index=str, columns=colmapper)
        df['Tally'] = df['Tally'].apply(lambda x: int(x))
        return df
    else:
        colmapper = dict(zip(range(11), colnames))
        df = df.iloc[1:].rename(index=str, columns=colmapper)
        df['Tally'] = df['Tally'].apply(lambda x: int(x))
        return df
		
def fix_election_file(fname_in, fname_out, candidates_as_columns = False):
    if candidates_as_columns == True:
        df = transform_election(load_election_df(fname_in))
    else:
        df = load_election_df(fname_in)
    df.to_csv(fname_out, index=False)
	
def concat_AD_ED(df):
    name_concat=(lambda row: reduce(lambda x,y: x + y, row))
    df['AD'] = df['AD'].apply(lambda x: str(x))
    df['ED'] = df['ED'].apply(lambda x: str(x))
    df['ED']=df['ED'].apply(lambda x: '0'*(3 - len(x)) + x)
    df['elect_dist']=df[['AD', 'ED']].apply(lambda x: name_concat(x), axis=1)
    return df

def transform_election(AD):
    unwanted_unit_name = ['Public Counter', 'Manually Counted Emergency', 'Emergency', 'Absentee / Military', 'Absentee/Military', 'Federal', 'Affidavit', 'Scattered']
    unit_name_values = AD['Unit Name'].unique().tolist()
    AD=AD[AD['Unit Name'].apply(lambda x: x not in unwanted_unit_name)]
    AD = concat_AD_ED(AD)
    #AD = AD[AD['Unit Name'].apply(lambda x: x not in unwanted_unit_name)]
    AD_EDs=AD['elect_dist'].unique().tolist()
    totals_by_ed=AD.groupby(by='elect_dist')['Tally'].sum()
    candidates=AD['Unit Name'].unique().tolist()
    candidate_mask_list=[AD['Unit Name'].apply(lambda x: x == candidate) for candidate in candidates]
    candidate_tally_list=[AD['Tally'][candidate_mask].reset_index(drop=True) for candidate_mask in candidate_mask_list]
    candidate_df=pd.DataFrame(candidate_tally_list).transpose()
    candidate_df.columns=candidates
    candidate_df.index = AD_EDs
    candidate_df['elect_dist'] = AD_EDs
    candidate_df['Total'] = totals_by_ed
    candidates_percent = [candidate + ' % of ED' for candidate in candidates]
    temp_pct=[100*candidate_df[candidate]/candidate_df['Total'] for candidate in candidates]
    candidate_df[candidates_percent] = pd.DataFrame(temp_pct).transpose()
    return candidate_df
def turn_AD_into_GDF(AD, EDs):
    unwanted_unit_name = ['Public Counter', 'Manually Counted Emergency', 'Emergency', 'Absentee / Military', 'Absentee/Military', 'Federal', 'Affidavit', 'Scattered']
    unit_name_values = AD['Unit Name'].unique().tolist()
    AD=AD[AD['Unit Name'].apply(lambda x: x not in unwanted_unit_name)]
    ### CONCATENATE AD, ED COLUMNS INTO ONE, elect_dist
    ### SAVE THE APPROPRIATE ADEDS INTO AD_EDs
    ### USE THOSE TO MASK THE GEODATAFRAME EDs; STORE AS EDs_AD
    ### CALCULATE THE VOTE TOTALS BY ED, STORE AS totals_by_ed
    AD = concat_AD_ED(AD)
    AD = AD[AD['Unit Name'].apply(lambda x: x not in unwanted_unit_name)]
    AD_EDs=AD['elect_dist'].unique().tolist()
    EDs['elect_dist']=EDs['elect_dist'].apply(lambda x: str(int(x)))
    mask = EDs['elect_dist'].apply(lambda x: x in AD_EDs)
    ### MASKING OUR GEODATAFRAME BY SELECTING ONLY THE EDS FROM THIS RACE
    EDs_AD=EDs[mask]
    totals_by_ed=AD.groupby(by='elect_dist')['Tally'].sum()
    ### STORE CANDIDATE NAMES AS candidates; THESE ARE JUST THE UNIQUE VALUES REMAINING IN THE Unit Name COLUMN
    ### THEN WE USE THE CANDIDATE NAMES TO MASK AD TO CREATE THEIR SEPARATE TALLIES AS candidate_tally_list;
    ### FINALLY WE MAKE A DATAFRAME OF CANDIDATE DATA candidate_df
    candidates=AD['Unit Name'].unique().tolist()
    candidate_mask_list=[AD['Unit Name'].apply(lambda x: x == candidate) for candidate in candidates]
    candidate_tally_list=[AD['Tally'][candidate_mask].reset_index(drop=True) for candidate_mask in candidate_mask_list]
    candidate_df=pd.DataFrame(candidate_tally_list).transpose()
    ### NAME COLUMNS OF candidate_df BY CANDIDATE NAMES, INDEX BY AD_EDs,
    ### AND COPY INDEX AS elect_dist, AND PUT TOTALS BY ED AS Total 
    candidate_df.columns=candidates
    candidate_df.index = AD_EDs
    candidate_df['elect_dist'] = AD_EDs
    candidate_df['Total'] = totals_by_ed
    ### THESE ARE FOR COLUMN NAMES OF NEW COLUMNS
    candidates_percent = [candidate + ' % of ED' for candidate in candidates]
    candidates_percent_total = [candidate + ' % of Total' for candidate in candidates]
    temp_pct=[100*candidate_df[candidate]/candidate_df['Total'] for candidate in candidates]
    candidate_df[candidates_percent] = pd.DataFrame(temp_pct).transpose()
    vote_total = candidate_df['Total'].sum()
    temp_pct_total = pd.DataFrame([100*candidate_df[candidate]/vote_total for candidate in candidates]).transpose()
    candidate_df[candidates_percent_total] = temp_pct_total
    EDs_AD=EDs_AD.set_index('elect_dist', drop=True)
    EDs_AD[candidate_df.columns] = candidate_df
    return EDs_AD
def load_election(fname, candidates_as_columns = False):
    if candidates_as_columns == True:
        return transform_election(load_election_df(fname))
    else:
        return load_election_df(fname)