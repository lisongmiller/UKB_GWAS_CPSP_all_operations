##################################################
## This script is to define CPSP phenotype after minor operations
##################################################
## {License_info}
##################################################
## Author: Song Li
## Copyright: Copyright {year}, {project_name}
## Credits: [{credit_list}]
## License: {license}
## Version: {minor}.{minor}.{rel}
## Mmaintainer: {maintainer}
## Email: {contact_email}
## Status: {dev_status}
##################################################


import os
import pandas as pd
import numpy as np
import datetime
os.chdir('/home/miller/PhD_project/UKB_CPSP_allop/scr')

###Part A: extract operation date
##A1: HR date
#import HR data, which alrady subset by operation
hr_opdate = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/1.operation_demo_subset/popu_opdate_minor.csv.gz', sep=',', dtype=str)

hr_opdate = hr_opdate.drop(['op_date'],axis='columns')
hr_opdate = hr_opdate.drop_duplicates(['n_eid','first_opdate','Category'])
hr_opdate = hr_opdate.set_index('n_eid',drop=False)
QC0_rm = hr_opdate.index[hr_opdate.index.duplicated(keep=False)] # #mark all duplicated eid index as TRUE, and extract all duplicated eid index
QC0_rm = QC0_rm.drop_duplicates()

##convert operation date to ymd, patients with operation data before date cut-off were already removed in SAS
hr_opdate['first_opdate'] = hr_opdate['first_opdate'].apply(pd.to_numeric, errors='coerce')
def sas_date(indate):
    ymddate = pd.to_timedelta(indate, unit='D') + pd.Timestamp('1960-1-1')
    ymddate = ymddate.strftime('%Y-%m-%d')
    return ymddate
hr_opdate['opdate_ymd'] = hr_opdate.first_opdate.apply(lambda x: sas_date(x))
hr_opdate['opdate_datetime'] =  hr_opdate.opdate_ymd.apply(lambda x:  pd.to_datetime(x))


'''
analgesic prescrption records were extracted in R in Snellius
GP_drug_code.to_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/3.analgesic_code/GP_drug_code.csv',sep=',',index=False,header=True)
'''

###Part C: QC
##C0: QC: remove patients with operation date before cut-off or invalid
#already done in SAS when extracting data

##C1: QC data: remove  patients without any prescription record
allop_eid_withanypres = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/2.allop_analgesic_gp_pres/allop_anypres_eid.txt.gz',sep='\t',dtype=str)
allop_eid_withanypres = allop_eid_withanypres.drop_duplicates(['eid'])

hr_opdate['eid'] = hr_opdate.index
QC1_rm = hr_opdate[~hr_opdate.eid.isin(allop_eid_withanypres.eid)]
QC1_rm = QC1_rm.assign(qcstep=1)
hr_opdate = hr_opdate[hr_opdate.eid.isin(allop_eid_withanypres.eid)]

del[allop_eid_withanypres]

## C2: Remove patients with another operation during 1-year follow up
## already done in Snellius R script

### C3: exclude patients with first operation after June 2015
#latest prescriptions end in June 2016, which is gp3. as gp3 with most subjects, so just set a uniform cut-off for convience
## already done in Snellius R script



### C4: remove subjects who died during 1-year follow-up
'''
#As s_40000_0_0 include all info in s_40000_1_0, so just use s_40000_0_0 is enough. 
'''
#already done in Snellius R script

### C5: keep subject who pass other sample QC
##already done in Snellius R script

### C6: QC analgesic prescription record for later phenotype file generation
anal_scr_date = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/2.allop_analgesic_gp_pres/gp_allop_pres.txt.gz',sep='\t', dtype = str)

##QC: remove prescription record without date
anal_scr_date = anal_scr_date[anal_scr_date.issue_date.apply(lambda x: type(x)!=float)]

##keep eid of scripts data in QCed list
anal_scr_date = anal_scr_date[anal_scr_date.eid.isin(hr_opdate.eid)]
anal_scr_date = anal_scr_date.drop_duplicates(['eid','issue_date','drug_name'])
anal_scr_date['dt'] = pd.to_datetime(anal_scr_date.issue_date) #transform date as the same format as operation data
anal_scr_date['issue_date'] = anal_scr_date.dt.astype(str)
anal_scr_date = anal_scr_date.drop('dt',axis = 'columns')
anal_scr_date = anal_scr_date.sort_values(by = ['eid','issue_date'])


###Part D: create CPSP phenotype
##D1: mark first analgesic record for each eid
anal_scr_date = anal_scr_date.set_index('eid',drop=False)
anal_scr_date['flag'] = np.where((anal_scr_date.eid != anal_scr_date.eid.shift()), 1, 0) #mark first analgesic records

#prepare eid with unique and duplicated presscription records separately
dup_index_list = anal_scr_date.index[anal_scr_date.index.duplicated(keep=False)] # #mark all duplicated eid index as TRUE, and extract all duplicated eid index
dup_index_list = dup_index_list.drop_duplicates()
dup_scr_date = anal_scr_date.loc[dup_index_list].apply(lambda x: '/'.join(anal_scr_date.loc[x['eid'],'issue_date']), axis = 1)
# '/'.join(['2012-01-11']) is all right, but '/'.join('2012-01-11') will goes wrong
#x is slice of anal_scr_date, [x['eid'],'issue_date'] select all issue_date under this eid, only join if x['flag'] == 1
dup_scr_date = dup_scr_date[dup_scr_date != '']
dup_scr_date = dup_scr_date.to_frame(name = 'issue_date')
dup_scr_date['eid'] = dup_scr_date.index
dup_scr_date = dup_scr_date.drop_duplicates(subset = 'eid')

uni_index_list = anal_scr_date.index[~anal_scr_date.index.isin(dup_index_list)]
uni_scr_date =  anal_scr_date.loc[uni_index_list,['eid','issue_date']]
gp_scr_date = pd.concat([dup_scr_date,uni_scr_date]) # concatenate temp with chem by row

##D2: merge with operatation data, select scripts date in range, and create final dataset adding prescription date as day-distance from operation
gp_scr_date['issue_dt_spl'] = gp_scr_date.issue_date.str.split('/')
gp_scr_date['issue_datetime'] =  gp_scr_date.issue_dt_spl.apply(lambda x:  pd.to_datetime(x))
gp_scr_date = gp_scr_date.reset_index(drop=True)
hrgp_op_scr = hr_opdate.merge(gp_scr_date, how='outer', on = 'eid')

hrgp_op_scr_nan = hrgp_op_scr[hrgp_op_scr.issue_date.isna()]
hrgp_op_scr_yes = hrgp_op_scr[-hrgp_op_scr.eid.isin(hrgp_op_scr_nan.eid)]
hrgp_op_scr_yes['diff_issue_ope'] = hrgp_op_scr_yes.apply(lambda x: x['issue_datetime'] - x['opdate_datetime'],axis = 1)
##np.where return index, then use index to obtain days
hrgp_op_scr_yes['pres_inrange'] = hrgp_op_scr_yes.diff_issue_ope.apply(lambda x: x[np.where(
    (x >=  datetime.timedelta(-360)) &
    (x <=  datetime.timedelta(360)))])

hrgp_op_scr_yes['pres_inrange'] = hrgp_op_scr_yes.pres_inrange.apply(lambda x: '/'.join(x[~x.isna()].astype(str))) #MERGING IN ONE COLUMN THE DATES #DataFrame.apply(,axis indicate application of function to each row.)
hrgp_op_scr_yes = hrgp_op_scr_yes.loc[:,['eid','opdate_datetime','pres_inrange']]
hrgp_op_scr_nan = hrgp_op_scr_nan.loc[:,['eid','opdate_datetime']]
hrgp_op_scr = pd.concat([hrgp_op_scr_yes,hrgp_op_scr_nan]) # concatenate temp with chem by row
hrgp_op_scr['pres_inrange'] = hrgp_op_scr.pres_inrange.str.replace(" days", "")


##D3: create varibles to define CPSP pheontype
##D31: for eid without pres record
hrgp_op_scr['status'] = ''
cpsp_ctr_nopres = hrgp_op_scr[hrgp_op_scr.pres_inrange.isna()|  (hrgp_op_scr['pres_inrange']== "")]

cpsp_ctr_nopres = cpsp_ctr_nopres.assign(status= '1',
                                         pre_scr_sum = 0,
                                         post_scr_sum = 0,
                                         pre_mon = 0,
                                         post_mon = 0)
##assign status for phenotype definition;eid with no prescriptions is considered as control

##D32: for eid with pres record
hrgp_op_scr_pres = hrgp_op_scr[~hrgp_op_scr.eid.isin(cpsp_ctr_nopres.eid)]

#def function to sum pres numbers in each month
def pres_per_month(pres_nr):
    pres_dict = {}
    for i in range(-12, 12): #zero key, right edge is not included
        pres_dict [i + 0.5] = len([p for p in pres_nr if int(p) // 30 == i])
    return pres_dict

#count pain prescription for each month
hrgp_op_scr_pres = hrgp_op_scr_pres.assign(pres_sum = hrgp_op_scr_pres.pres_inrange.str.split('/').apply(pres_per_month))

#######
os.chdir('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/CPSP_phenotype/minor')

###prescription number distribution
hrgp_op_scr_pres_demo = hrgp_op_scr_pres
pre_item = [-11.5,-10.5,-9.5,-8.5,-7.5,-6.5,-5.5,-4.5,-3.5,-2.5,-1.5,-0.5]
post_item = [0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5]

hrgp_op_scr_pres_demo = hrgp_op_scr_pres_demo.assign(
    pre_scr = hrgp_op_scr_pres_demo.pres_sum.apply(lambda x: {i: x[i] for i in pre_item}),
    post_scr = hrgp_op_scr_pres_demo.pres_sum.apply(lambda x: {i: x[i] for i in post_item})
)
hrgp_op_scr_pres_demo = hrgp_op_scr_pres_demo.assign(
    pre_scr_sum = hrgp_op_scr_pres_demo.pre_scr.apply(lambda x: sum(x.values())),
    post_scr_sum = hrgp_op_scr_pres_demo.post_scr.apply(lambda x: sum(x.values()))
)
hrgp_op_scr_pres_demo = hrgp_op_scr_pres_demo.assign(
    pre_mon = hrgp_op_scr_pres_demo.pres_sum.apply(lambda x: (len([e for e in x if e<0 if x[e]!=0]))),
    post_mon = hrgp_op_scr_pres_demo.pres_sum.apply(lambda x: (len([e for e in x if e>0 if x[e]!=0])))
)


###D4: define CPSP phenotype
###define case and control, pre_mon < 3 and post_mon covered 0 < x <= 3. 3< x <= 6. 6 < x;
QC2_rm = hrgp_op_scr_pres_demo[hrgp_op_scr_pres_demo['pre_mon'] > 3]
QC2_rm['qcstep'] = 2
QC_rm = pd.concat([QC1_rm[["eid", "qcstep"]],QC2_rm[["eid", "qcstep"]]])

QC_rm.to_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/CPSP_phenotype/minor/qc_rm.txt',sep='\t',index=False)

hrgp_op_scr_pres_demo_clean = hrgp_op_scr_pres_demo[~hrgp_op_scr_pres_demo.eid.isin(QC_rm.eid)]

hrgp_op_scr_pres_demo_clean.status[hrgp_op_scr_pres_demo_clean['post_mon'] > 6] = '3'
hrgp_op_scr_pres_demo_clean.status[(hrgp_op_scr_pres_demo_clean['post_mon'] > 3) & (hrgp_op_scr_pres_demo_clean['post_mon'] <= 6)] = '2'
hrgp_op_scr_pres_demo_clean.status[hrgp_op_scr_pres_demo_clean['post_mon'] <= 3] = '1'

cpsp_pheno_final = pd.concat([hrgp_op_scr_pres_demo_clean,cpsp_ctr_nopres])

freq = cpsp_pheno_final['status'].value_counts()
print(freq)

#Add surgery category
hr_opdate['eid'] = hr_opdate['eid'].astype(int)
hr_opdate = hr_opdate.loc[:, ['eid', 'Category']]
hr_opdate = hr_opdate.reset_index(drop=True)
hr_opdate['eid'] = hr_opdate['eid'].astype(str)

cpsp_pheno_final = cpsp_pheno_final.merge(hr_opdate, how='left', on = 'eid')
freq = cpsp_pheno_final['Category'].value_counts()
print(freq)

cpsp_pheno_final.to_csv('./cpsp_phenotype_minor.txt.gz',sep='\t',index=False)

#check opioid user
GP_drug_code = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/3.analgesic_code/GP_drug_code.csv',sep=',')
GP_drug_code = GP_drug_code[GP_drug_code['Category'] == 'OPIOID']

anal_scr_date = anal_scr_date.reset_index(drop=True)
anal_scr_date['eid'] = anal_scr_date['eid'].astype(int)
anal_scr_date_opioid = anal_scr_date[anal_scr_date['drug_name'].isin(GP_drug_code['drug_name'])]
anal_scr_date_opioid['n_opioid'] = anal_scr_date_opioid.groupby('eid')['drug_name'].transform('size')
anal_scr_date_opioid = anal_scr_date_opioid.drop_duplicates(['eid','n_opioid'])
anal_scr_date_opioid = anal_scr_date_opioid[['eid', 'n_opioid']]

#Create binary phenotype
anal_scr_date_opioid['eid'] = anal_scr_date_opioid['eid'].astype(str)
cpsp_pheno_final_test1 = cpsp_pheno_final.copy()
cpsp_pheno_final_test1['pheno'] = np.where(cpsp_pheno_final_test1['status'] == '1', 1, 2)

cpsp_pheno_final_test2 = cpsp_pheno_final_test1.merge(anal_scr_date_opioid, how='left', on = 'eid')
cpsp_pheno_final_test2['opfl'] = np.where(cpsp_pheno_final_test2['n_opioid'].isna(), 0, 1) #mark first analgesic records

table = pd.crosstab(cpsp_pheno_final_test2['pheno'], cpsp_pheno_final_test2['opfl'])
print(table)
table_row_percentages = table.div(table.sum(axis=1), axis=0) * 100
# Print the row percentages of opioid use
print(table_row_percentages)

# Print opioid prescription numbers
grouped = cpsp_pheno_final_test2.groupby('pheno')
median = grouped['n_opioid'].median()
std_dev = grouped['n_opioid'].std()

print(median)
print(std_dev)

# Print post-analgesic prescription numbers
grouped = cpsp_pheno_final_test2.groupby('pheno')
median = grouped['post_scr_sum'].median()
std_dev = grouped['post_scr_sum'].std()

print(median)
print(std_dev)

# Print post-analgesic prescription months
grouped = cpsp_pheno_final_test2.groupby('pheno')
median = grouped['post_mon'].median()
std_dev = grouped['post_mon'].std()

print(median)
print(std_dev)

cpsp_pheno_final_test2.to_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/CPSP_phenotype/minor/cpsp_pheno_final_test2.txt.gz',sep='\t',index=False)


