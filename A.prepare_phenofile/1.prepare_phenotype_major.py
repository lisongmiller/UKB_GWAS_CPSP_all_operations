##################################################
## This script is to generate GWAS phenotype file
##################################################
## {License_info}
##################################################
## Author: Song Li
## Copyright: Copyright {year}, {project_name}
## Credits: [{credit_list}]
## License: {license}
## Version: {mayor}.{minor}.{rel}
## Mmaintainer: {maintainer}
## Email: {contact_email}
## Status: {dev_status}
##################################################

import os
import pandas as pd
import numpy as np
from collections import Counter
os.chdir('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major')

###Chapter A: create covariate variables
##A1: preparing demographic file
# select variables for demographic data
list_var = ['n_eid','n_34_0_0','n_54_0_0','n_22000_0_0','n_31_0_0',
            list(map('n_21001_{}_0'.format, np.arange(4))),
            list(map('n_22009_0_{}'.format, np.arange(1,11))),
            list(map('n_3799_{}_0'.format, np.arange(4))),
            list(map('n_4067_{}_0'.format, np.arange(4))),
            list(map('n_3404_{}_0'.format, np.arange(4))),
            list(map('n_3571_{}_0'.format, np.arange(4))),
            list(map('n_3741_{}_0'.format, np.arange(4))),
            list(map('n_3414_{}_0'.format, np.arange(4))),
            list(map('n_3773_{}_0'.format, np.arange(4))),
            list(map('n_2956_{}_0'.format, np.arange(4))),
            ]

# function used for removing nested lists in python.
# output list
flat_list = []
def reemovNestings(l):
    for i in l:
        if type(i) == list:
            reemovNestings(i)
        else:
            flat_list.append(i)

reemovNestings(list_var)
list_var = flat_list


demographic = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/1.operation_demo_subset/popu_op_demo.csv.gz',sep=',', dtype=str,usecols=list_var)

#subset demo file by selecting eid in phenotype file
#import CPSP phenotype file
cpsp_pheno_final = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/CPSP_phenotype/major/cpsp_phenotype_major.txt.gz',sep='\t',dtype=str)
#distribution of phenotype
freq = cpsp_pheno_final['status'].value_counts()
print(freq)

#select CPSP eid from hr first, then select eid from gp
demographic = demographic[demographic.n_eid.isin(cpsp_pheno_final.eid)]
demographic = demographic.rename(columns={"n_eid": "eid"})

demographic = demographic.drop_duplicates()
demographic = demographic.set_index('eid',drop=False)

##A2: define covariate: CHIP
def modify_chip(x):
    if int(x)>0:
        return 'T2000'
    return 'T1000'
demographic['CHIP'] = demographic.n_22000_0_0.apply(lambda x: modify_chip(x))

##A3: define covariate: CENTER
demographic['CENTER'] = np.array(demographic['n_54_0_0'].apply(lambda x: 'T'+x))

##A4: define covariate: SEX
demographic['SEX'] = np.array(demographic['n_31_0_0'])

##A5: define BMI
#def a function to select the first non-missing value
def select_first(df):
    if df.first_valid_index() is None:
        return float('NaN')
    else:
        return df[df.first_valid_index()]

demo_subset = demographic.loc[:, list(map('n_21001_{}_0'.format, np.arange(4)))]
demographic['BMI'] = demo_subset.apply(select_first, axis=1)
demographic.reset_index(drop=True, inplace=True)


'''
##A5: define chronic pain
#def a function to select if pain value exist
pain_list  = [
            list(map('n_3571_{}_0'.format, np.arange(4))),
            list(map('n_3741_{}_0'.format, np.arange(4))),
            ]
flat_list = []
reemovNestings(pain_list)
pain_list = flat_list

del demo_subset
demo_subset = demographic.loc[:, pain_list]

#define back pain
demo_subset['back_pain_temp1'] = demo_subset.iloc[:,0:4].apply(lambda x: list(int(i) for i in x if pd.notnull(i)), axis=1)
demo_subset['back_pain_temp2'] = demo_subset.back_pain_temp1.apply(lambda x: list(np.unique(x)))

def select_anypain(var1):
    if var1 == [0]:
        return 'no'
    elif np.isin(1, var1):
        return 'yes'
    else:
        return ''

demo_subset['back_pain'] = demo_subset.back_pain_temp2.apply(lambda x: select_anypain(x))
freq = demo_subset['back_pain'].value_counts()
print(freq)

#define abd pain
demo_subset['abd_pain_temp1'] = demo_subset.iloc[:,4:8].apply(lambda x: list(int(i) for i in x if pd.notnull(i)), axis=1)
demo_subset['abd_pain_temp2'] = demo_subset.abd_pain_temp1.apply(lambda x: list(np.unique(x)))

demo_subset['abd_pain'] = demo_subset.abd_pain_temp2.apply(lambda x: select_anypain(x))
freq = demo_subset['abd_pain'].value_counts()
print(freq)

demo_subset = demo_subset.loc[:,['back_pain','abd_pain']]
demographic_temp = pd.merge(demographic, demo_subset, left_index=True, right_index=True)
demographic_temp.reset_index(drop=True, inplace=True)


##A6: define CPSP phenotype
add_data1 = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_abd/input/4.operation_demo_subset/raw_abd_operation/add_data1.tab.gz',sep='\t',
                             dtype=str,usecols=['ukb45875.tab','f.120005.0.0'])
add_data1 = add_data1.rename(columns={'ukb45875.tab' : "eid",'f.120005.0.0': 'n_120005_0_0'})

def select_CPSP(var1):
    if var1 == '0':
        return 'no'
    elif var1 == '1':
        return 'yes'
    else:
        return ''

add_data1['CPSP'] = add_data1.n_120005_0_0.apply(lambda x: select_CPSP(x))
demographic_temp = pd.merge(demographic_temp,add_data1,how='left',on = 'eid')
'''

##A7: define age at operation covariate
cpsp_pheno_final = pd.merge(cpsp_pheno_final,demographic,how='left',on = 'eid')
cpsp_pheno_final['age_at_operation'] = cpsp_pheno_final.apply(lambda x: int(x['opdate_datetime'][0:4]) - int(x['n_34_0_0']),axis =1)

##A8: output file for covar check
cpsp_pheno_covarcheck = cpsp_pheno_final.loc[:,['eid','status','age_at_operation','BMI','SEX','pre_scr_sum','post_scr_sum', 'Category']]
cpsp_pheno_covarcheck.to_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/check_covar/major/cpsp_pheno_covarcheck.txt',header = True, index = False, sep = '\t')



##A9: prepare ordinal GWAS inputput file
#generate ordinal phenotype file

phenofile = cpsp_pheno_final.loc[:,['eid','status']]
phenofile['FID'] = phenofile.eid
phenofile['IID'] = phenofile.eid
phenofile['Pheno1'] = phenofile.status.apply(lambda x: str(int(x)))
phenofile = phenofile.loc[:,['FID','IID','Pheno1']]

#generate binary covar file
binary = cpsp_pheno_final.loc[:,['eid','SEX','CENTER','CHIP','Category']]
binary['FID'] = binary.eid
binary['IID'] = binary.eid
binary = binary.loc[:,['FID','IID','SEX','CENTER','CHIP','Category']]

list_var = ['eid','age_at_operation',list(map('n_22009_0_{}'.format, np.arange(1,11)))]
flat_list = []
reemovNestings(list_var)
list_var = flat_list


#generate continuous covar file
continuous = cpsp_pheno_final.loc[:,list_var]
continuous['FID'] = continuous.eid
continuous['IID'] = continuous.eid
list_var = ['FID','IID','age_at_operation',list(map('n_22009_0_{}'.format, np.arange(1,11)))]
flat_list = []
reemovNestings(list_var)
list_var = flat_list
continuous = continuous.loc[:,list_var]

phenofile.to_csv('./ordinal/ordinal_pheno_lmm.txt',sep='\t',index=False,header=True)
binary.to_csv('./ordinal/ordinal_covarb_lmm.txt',sep='\t',index=False,header=True)
continuous.to_csv('./ordinal/ordinal_covarc_lmm.txt',sep='\t',index=False,header=True)


##A10: prepare binary GWAS inputput file
phenofile['Pheno_b'] = np.where(phenofile.Pheno1.isin(['1']),'1','2')

phenofile_binary = phenofile.loc[:,['FID','IID','Pheno_b']]
phenofile_binary.to_csv('./binary/binary_pheno_lmm.txt',sep='\t',index=False,header=True)
binary.to_csv('./binary/binary_covarb_lmm.txt',sep='\t',index=False,header=True)
continuous.to_csv('./binary/binary_covarc_lmm.txt',sep='\t',index=False,header=True)
