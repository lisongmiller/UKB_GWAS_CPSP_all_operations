#!/bin/bash
#Set job requirements
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --partition=thin
#SBATCH --time=00:30:00

##The job takes one chromosome and will use 24 cores to analyse it.
##This job is to generate dosage from UKB imputed genotype


##Creating directories to store the output data
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/LMM_major/output



##define genofile, phenofile, covarfile
phenoFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_major/binary_pheno_lmm.txt"
phenoFile=$(basename -- "$phenoFileFull")
covarbFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_major/binary_covarb_lmm.txt"
covarbFile=$(basename -- "$covarbFileFull")
covarcFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_major/binary_covarc_lmm.txt"
covarcFile=$(basename -- "$covarcFileFull")
genoFileFull=/gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen

##Going into the TMPDIR to run the analyse
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/LMM_major

##copy files to current folder
#copy pheno
cp "$phenoFileFull" ./
#copy binary covar
cp "$covarbFileFull" ./
#copy continuous covar
cp "$covarcFileFull" ./
#copy gcta
cp "$HOME"/software/gcta/gcta-1.94.1-linux-kernel-3-x86_64/gcta64 ./
#copy genofile
cp "$genoFileFull"/ukb_imp_pf_chr* ./

for index in `seq 1 22`; do echo ukb_imp_pf_chr$index >> bgen.txt; done
#copy sparce GRM
cp  "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/grm/sp_grm* ./


# fastGWA mixed model (based on the sparse GRM generated above)
./gcta64 --mbgen bgen.txt \
--sample ukb_imp_pf_chr1.sample \
--grm-sparse sp_grm \
--fastGWA-mlm \
--pheno "$phenoFile" \
--threads 60 \
--maf 0.005 \
--qcovar "$covarcFile" \
--covar "$covarbFile" \
--out output/geno_assoc_LMM_major





## Another check incase something went wrong
#ls -lha >> ukb_gcta_LMM_major.log

##Copying the output to your home folder
cp ./*.log    "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/assoc
cp ./output/* "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/assoc
