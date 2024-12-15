#!/bin/bash
#Set job requirements
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --partition=fat
#SBATCH --time=12:00:00

##The job takes one chromosome and will use 24 cores to analyse it.
##This job is to generate dosage from UKB imputed genotype


##Going into the TMPDIR to run the analyse
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_minor/LMM_minor

##define genofile, phenofile, covarfile
phenoFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_minor/binary_pheno_lmm.txt"
phenoFile=$(basename -- "$phenoFileFull")
covarbFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_minor/binary_covarb_lmm.txt"
covarbFile=$(basename -- "$covarbFileFull")
covarcFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_minor/binary_covarc_lmm.txt"
covarcFile=$(basename -- "$covarcFileFull")
#genoFileFull=/gpfs/scratch1/shared/songli/CPSP_allop/LMM_minor/input/bgen

#cp /gpfs/scratch1/shared/songli/CPSP_allop/LMM_minor/mkGRM/full_dense_grm* ./

# fastGWA mixed model (based on the sparse GRM generated above)
./gcta64 --grm full_dense_grm \
--reml \
--pheno "$phenoFile" \
--covar "$covarbFile" \
--qcovar "$covarcFile" \
--threads 128 \
--out output/GREML_minor


##Copying the output to your home folder
cp ./output/GREML_minor* "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_minor/GREML