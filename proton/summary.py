import pandas as pd

#
# PROTON
# (C) 2022-2042, Kumar Madhukar
# Department of Computer Science and Engineering, Indian Institute of Technology Delhi
#


# Load the Excel file
file_path = '/home/u312809/Desktop/bounty-svcomp.xlsx'
df = pd.read_excel(file_path, sheet_name='Bounty-SVCOMP-24-NT', skiprows=2)

# Rename the columns for better clarity
df.columns = [
    'FULL Name', 'FOLDER', 'FILE', 'BRESULT', 'BTIME', 'BMEM', 'UNWIND', 
    'Bstatus', 'RSA', 'LRESULT', 'LTIME', 'LMEM', 'CRESULT', 'CTIME', 'CMEM', 
    'URESULT', 'UTIME', 'UMEM'
]

# Drop rows with missing 'Full Name'
df = df.dropna(subset=['FULL Name'])

# Summarize subtotals and break down results
#summary = df.groupby(['FOLDER']).size().reset_index(name='Count')
#summary = df.groupby(['FOLDER','BRESULT', 'LRESULT', 'CRESULT', 'URESULT']).size().reset_index(name='Count')

# Save the summary to a new Excel file
#summary.to_excel('/home/u312809/Downloads/termination-main/tools/proton/summary.xlsx', index=False)


# Define the columns to summarize
columns_to_summarize = ['BRESULT', 'BTIME', 'RSA', 'LRESULT', 'LTIME', 'CRESULT', 'CTIME', 'URESULT', 'UTIME']

# Initialize a dictionary to store the summary dataframes
summary_dfs = {}

# Loop through each column and compute the summary
for column in columns_to_summarize:
    summary = df.groupby(['FOLDER', column]).size().reset_index(name='Count')
    pivot_summary = summary.pivot(index='FOLDER', columns=column, values='Count').fillna(0)
    summary_dfs[column] = pivot_summary

# Combine all summary dataframes into one
combined_summary = pd.concat(summary_dfs, axis=1)

# Save the combined summary to a new Excel file
combined_summary.to_excel('/home/u312809/Downloads/termination-main/tools/proton/combined_summary.xlsx')

print(summary)
