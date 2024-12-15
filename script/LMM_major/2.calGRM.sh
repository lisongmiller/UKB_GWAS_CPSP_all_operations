#!/bin/bash
#Set job requirements
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --partition=thin
#SBATCH --time=03:00:00


##The job is to make GRM and will use 24 cores to analyse it.
##Create a job with a for loop like:
#for part in {2..10}; do sbatch 2.calGRM.sh $part; done





##################
###Following code only run once: copy gcta and copy genofile
##################
<<com
##Creating directories to store the output data
mkdir -p /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/mkGRM

##Going into the TMPDIR to run the analyse
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/mkGRM

cp "$HOME"/software/gcta/gcta-1.94.1-linux-kernel-3-x86_64/gcta64 ./
genoFileFull=/gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/input/bgen
cp "$genoFileFull"/* ./
for index in `seq 1 22`; do echo ukb_imp_pf_chr$index >> bgen.txt; done
com
##################


##################
###Following code run 10 times
##Part 1 Running gcta64, calculate dense grm
##################
<<com

part=$1
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/mkGRM

./gcta64 --mbgen bgen.txt --sample ukb_imp_pf_chr1.sample  --make-grm-part 10 "$part" --threads 60 --out full_dense_grm 

com

##################
###Following code run once
###part 2: merge together and set threshold. Run this part only when all results of part1 is finished
##################

##merge GRM_temp file together
cd /gpfs/scratch1/shared/songli/CPSP_allop/LMM_major/mkGRM

cat full_dense_grm.part_10_*.grm.id > full_dense_grm.grm.id
cat full_dense_grm.part_10_*.grm.bin > full_dense_grm.grm.bin
cat full_dense_grm.part_10_*.grm.N.bin > full_dense_grm.grm.N.bin

##set threshold to keep sparse grm
./gcta64 --grm full_dense_grm --make-bK-sparse 0.05 --out sp_grm

##Copying the output to your home folder
cp ./*.log "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/grm
cp ./sp_grm* "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/grm
cp ./full_dense_grm.* "$HOME"/project/phd_project_ukb/UKB_Application64102/CPSP_allop/output/LMM_major/grm
