#!/usr/bin/env bash

mkdir logs

CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 2000 &> logs/00.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 2000 &> logs/10.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 2000 &> logs/02.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 2000 &> logs/03.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 2000 &> logs/04.log &

CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 2000 &> logs/10.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 2000 &> logs/11.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 2000 &> logs/12.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 2000 &> logs/13.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 2000 &> logs/14.log &