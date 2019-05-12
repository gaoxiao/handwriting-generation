#!/usr/bin/env bash

CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 10000 &> logs/0.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 10000 &> logs/1.log &
CUDA_VISIBLE_DEVICES=0 python gen_dataset.py --size 10000 &> logs/2.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 10000 &> logs/3.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 10000 &> logs/4.log &
CUDA_VISIBLE_DEVICES=1 python gen_dataset.py --size 10000 &> logs/5.log &