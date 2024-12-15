#!/bin/bash
#Set job requirements
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --partition=thin
#SBATCH --time=05:00:00

###This job is to extract genotype and perfrom QC
###The job takes 22 chromosome and will use 24 cores to analyse it.
##Create a job for every chromosome with a for loop like:
#for chromo in {1..21}; do sbatch 1.prepare_bgen_bed_for_LMM.sh $chromo; done

###Part1: make folders and assign variables

chromo=$1

phenoFileFull="$HOME/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_major/binary_pheno_lmm.txt"
phenoFile=$(basename -- "$phenoFileFull")
sampleFolder="/gpfs/work3/0/einf1831/Projects/UKB_Application64102/bulk_data/sample_files"


##Creating directories to store the output data
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/chr"$chromo"
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen_temp
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bed
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/output

##Going into the folder to run the analyse
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/chr"$chromo"
tempFolder=/gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen_temp



##Copying the pheno, covar and sample files.
cp $phenoFileFull ./
cp "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/input/LMM_major/control_eid_norel.txt ./
cp "$sampleFolder"/ukb*_imp_chr"$chromo"_*.sample ./
cp "$HOME"/software/plink/plink2_linux_x86_64_20220313/plink2 ./

##print out all the files in the working directory to the log file. In case you need to troubleshoot 
#ls -lha >> ukb_ls.log


###Part2: keep patients interested and prepare bgen 
##Running plink2, adjust the parameters to your needs
./plink2 --bgen /gpfs/work4/0/ukbb_nij/Gdata_v3/bgen/ukb_imp_chr"$chromo"_v3.bgen ref-first \
--sample ukb*_imp_chr"$chromo"_*.sample \
--keep $phenoFile \
--snps-only just-acgt \
--mind 0.1 \
--geno 0.05 \
--extract /gpfs/work4/0/ukbb_nij/ukbb_nij/maf_info/ukb_mfi_ALL_v3_KeepMAF005andINFO8 \
--export bgen-1.3 ref-first \
--out ../bgen_temp/temp_ukb_imp_pf_chr"$chromo"


##Running plink2, test HWE in controls only
tempFolder=/gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen_temp

./plink2 --bgen "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".bgen ref-first \
--sample "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".sample \
--hwe 1e-6 \
--pheno ./binary_pheno_lmm.txt \
--keep control_eid_norel.txt \
--make-just-bim \
--out "$tempFolder"/chr"$chromo"variants_passhwe

##Running plink2, export bgen
./plink2 --bgen "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".bgen ref-first \
--sample "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".sample \
--geno 0.05 \
--mind 0.1 \
--extract "$tempFolder"/chr"$chromo"variants_passhwe.bim \
--export bgen-1.3 ref-first \
--out ../bgen/ukb_imp_pf_chr"$chromo"

./plink2 --bgen "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".bgen ref-first \
--sample "$tempFolder"/temp_ukb_imp_pf_chr"$chromo".sample \
--geno 0.05 \
--mind 0.1 \
--extract "$tempFolder"/chr"$chromo"variants_passhwe.bim \
--make-bed \
--out ../bed/ukb_imp_pf_chr"$chromo"

##Making index for bgen file
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen
/gpfs/home1/songli/software/BGEN/bgen/build/apps/bgenix -g ukb_imp_pf_chr"$chromo".bgen -index

## Another check in case something went wrong
#ls -lha >> ukb_ls.log

##Copying the output to your home folder
##Remove the rm command if you want to access the used files after analyses. Files on scratch are automatically removed in ~7 days 



