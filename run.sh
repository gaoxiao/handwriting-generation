#!/usr/bin/env bash

mkdir logs

CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 50000 &> logs/00.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 50000 &> logs/01.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 50000 &> logs/02.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 50000 &> logs/03.log &

CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 50000 &> logs/10.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 50000 &> logs/11.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 50000 &> logs/12.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 50000 &> logs/13.log &

CUDA_VISIBLE_DEVICES=2 python gen_dataset.py --size 50000 &> logs/20.log &
CUDA_VISIBLE_DEVICES=2 python gen_dataset.py --size 50000 &> logs/21.log &
CUDA_VISIBLE_DEVICES=2 python gen_dataset.py --size 50000 &> logs/22.log &
CUDA_VISIBLE_DEVICES=2 python gen_dataset.py --size 50000 &> logs/23.log &

CUDA_VISIBLE_DEVICES=3 python gen_dataset.py --size 50000 &> logs/30.log &
CUDA_VISIBLE_DEVICES=3 python gen_dataset.py --size 50000 &> logs/31.log &
CUDA_VISIBLE_DEVICES=3 python gen_dataset.py --size 50000 &> logs/32.log &
CUDA_VISIBLE_DEVICES=3 python gen_dataset.py --size 50000 &> logs/33.log &