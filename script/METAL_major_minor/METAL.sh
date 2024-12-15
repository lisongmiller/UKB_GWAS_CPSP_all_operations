#!/bin/bash
#Set job requirements
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --partition=thin
#SBATCH --time=01:00:00

##This job is to run meta-analysis between CPSP after major and minor surgery

module load 2021

mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/metal_major_minor/output

cd /gpfs/scratch1/shared/songli/CPSP_allop/metal_major_minor

cp /gpfs/home1/songli/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/assoc/geno_assoc_LMM_major.fastGWA.gz ./
cp /gpfs/home1/songli/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_minor/assoc/geno_assoc_LMM_minor.fastGWA.gz ./

cp /gpfs/home1/songli/project/phd_project_ukb/UKB_Application64102/CPSP_allop/scr/METAL_major_minor/metal.txt ./

/gpfs/home1/songli/software/METAL/METAL-master/build/bin/metal ./metal.txt

cp /gpfs/scratch1/shared/songli/CPSP_allop/metal_major_minor/*_INV* /gpfs/home1/songli/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/meta_major_minor
