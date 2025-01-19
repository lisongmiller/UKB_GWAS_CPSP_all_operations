##################################################
## This script is to generate GWAS phenotype file for subtype GWAS
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
os.chdir('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/subtype')

###Part A: parepare subtype phenotypes
#import major operation phenotype file
phenofile_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/binary/binary_pheno_lmm.txt',sep='\t', dtype=str)
covarb_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/binary/binary_covarb_lmm.txt',sep='\t', dtype=str)
covarc_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/binary/binary_covarc_lmm.txt',sep='\t', dtype=str)

#import minor operation phenotype file
phenofile_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/binary/binary_pheno_lmm.txt',sep='\t', dtype=str)
covarb_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/binary/binary_covarb_lmm.txt',sep='\t', dtype=str)
covarc_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/binary/binary_covarc_lmm.txt',sep='\t', dtype=str)

# Concatenate vertically (along the rows)
phenofile = pd.concat([phenofile_ma,phenofile_mi])
covarb = pd.concat([covarb_ma,covarb_mi])
covarc = pd.concat([covarc_ma,covarc_mi])

#Drop last five PCs
covarc = covarc.rename(columns=lambda x: x.replace('n_22009_0_', 'PC'))
covarc = covarc.drop(['PC6','PC7','PC8','PC9','PC10'],axis='columns')

##Remove category as multiple
hr_opdate_uni = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/1.operation_demo_subset/popu_opdate_major_uni.csv.gz', sep=',', dtype=str)
hr_opdate_uni = hr_opdate_uni.drop(['OPCS4','op_date','first_opdate'],axis='columns')
hr_opdate_uni = hr_opdate_uni[hr_opdate_uni['n_eid'].isin(phenofile.IID)]

hr_opdate_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/1.operation_demo_subset/popu_opdate_minor.csv.gz', sep=',', dtype=str)
hr_opdate_mi_rm = hr_opdate_mi[hr_opdate_mi['Category'] == 'Multiple']
hr_opdate_mi = hr_opdate_mi[~hr_opdate_mi.n_eid.isin(hr_opdate_mi_rm.n_eid)]
hr_opdate_mi = hr_opdate_mi.drop(['op_date','first_opdate'],axis='columns')
hr_opdate_mi = hr_opdate_mi[hr_opdate_mi['n_eid'].isin(phenofile.IID)]

hr_opdate = pd.concat([hr_opdate_uni,hr_opdate_mi])

# Get the unique values from the 'City' column
op_types = hr_opdate.Category.unique()

# Create subsets based on unique values
hr_opdate_sub = {}
phenofile_sub = {}
covarc_sub = {}
covarb_sub = {}

for value in op_types:
    hr_opdate_sub[value] = hr_opdate[hr_opdate['Category'] == value]
    phenofile_sub[value] = phenofile[phenofile.IID.isin(hr_opdate_sub[value].n_eid)]
    covarc_sub[value] = covarc[covarc.IID.isin(hr_opdate_sub[value].n_eid)]
    covarb_sub[value] = covarb[covarb.IID.isin(hr_opdate_sub[value].n_eid)].drop(['Category'], axis='columns')


# Save each subset as a separate TXT file
for value, subset in phenofile_sub.items():
    filename = f"pheno_lmm_{value}.txt"
    subset.to_csv(filename, sep='\t', index=False, header=True)
    print(f"Subset for {value} saved as {filename}")

for value, subset in covarc_sub.items():
    filename = f"covarc_lmm_{value}.txt"
    subset.to_csv(filename, sep='\t', index=False, header=True)
    print(f"Subset for {value} saved as {filename}")

for value, subset in covarb_sub.items():
    filename = f"covarb_lmm_{value}.txt"
    subset.to_csv(filename, sep='\t', index=False, header=True)
    print(f"Subset for {value} saved as {filename}")



###Part B: parepare ordinal phenotype containing both major and minor operations
os.chdir('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/allop/ordinal')

###Part A: parepare subtype phenotypes
#import major operation phenotype file
phenofile_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/ordinal/ordinal_pheno_lmm.txt',sep='\t', dtype=str)
covarb_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/ordinal/ordinal_covarb_lmm.txt',sep='\t', dtype=str)
covarc_ma = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/major/ordinal/ordinal_covarc_lmm.txt',sep='\t', dtype=str)

#import minor operation phenotype file
phenofile_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/ordinal/ordinal_pheno_lmm.txt',sep='\t', dtype=str)
covarb_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/ordinal/ordinal_covarb_lmm.txt',sep='\t', dtype=str)
covarc_mi = pd.read_csv('/home/miller/PhD_project/UKB_CPSP_allop/input/4.phenotype_file/gwas_phenotype_file/minor/ordinal/ordinal_covarc_lmm.txt',sep='\t', dtype=str)

# Concatenate vertically (along the rows)
phenofile = pd.concat([phenofile_ma,phenofile_mi])
covarb = pd.concat([covarb_ma,covarb_mi])
covarc = pd.concat([covarc_ma,covarc_mi])

#Drop last five PCs
covarc = covarc.rename(columns=lambda x: x.replace('n_22009_0_', 'PC'))
covarc = covarc.drop(['PC6','PC7','PC8','PC9','PC10'],axis='columns')

phenofile.to_csv("./ordinal_pheno.txt", sep='\t', index=False, header=True)
covarb.to_csv("./ordinal_covarb.txt", sep='\t', index=False, header=True)
covarc.to_csv("./ordinal_covarc.txt", sep='\t', index=False, header=True)