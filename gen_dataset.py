import argparse
import os
import pickle
import random
import uuid
from collections import namedtuple

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--model', dest='model_path', type=str, default=os.path.join('pretrained', 'model-29'))
parser.add_argument('--text', dest='text', type=str, default=None)
parser.add_argument('--style', dest='style', type=int, default=None)
parser.add_argument('--bias', dest='bias', type=float, default=1.)
parser.add_argument('--force', dest='force', action='store_true', default=False)
parser.add_argument('--animation', dest='animation', action='store_true', default=False)
parser.add_argument('--save', dest='save', type=str, default=None)
parser.add_argument('--size', dest='size', type=int, default=100)
args = parser.parse_args()


def sample(e, mu1, mu2, std1, std2, rho):
    cov = np.array([[std1 * std1, std1 * std2 * rho],
                    [std1 * std2 * rho, std2 * std2]])
    mean = np.array([mu1, mu2])

    x, y = np.random.multivariate_normal(mean, cov)
    end = np.random.binomial(1, e)
    return np.array([x, y, end])


def split_strokes(points):
    points = np.array(points)
    strokes = []
    b = 0
    for e in range(len(points)):
        if points[e, 2] == 1.:
            strokes += [points[b: e + 1, :2].copy()]
            b = e + 1
    return strokes


def cumsum(points):
    sums = np.cumsum(points[:, :2], axis=0)
    return np.concatenate([sums, points[:, 2:]], axis=1)


def sample_text(sess, args_text, translation, style=None):
    fields = ['coordinates', 'sequence', 'bias', 'e', 'pi', 'mu1', 'mu2', 'std1', 'std2',
              'rho', 'window', 'kappa', 'phi', 'finish', 'zero_states']
    vs = namedtuple('Params', fields)(
        *[tf.get_collection(name)[0] for name in fields]
    )

    text = np.array([translation.get(c, 0) for c in args_text])
    coord = np.array([0., 0., 1.])
    coords = [coord]

    # Prime the model with the author style if requested
    prime_len, style_len = 0, 0
    if style is not None:
        # Priming consist of joining to a real pen-position and character sequences the synthetic sequence to generate
        #   and set the synthetic pen-position to a null vector (the positions are sampled from the MDN)
        style_coords, style_text = style
        prime_len = len(style_coords)
        style_len = len(style_text)
        prime_coords = list(style_coords)
        coord = prime_coords[0]  # Set the first pen stroke as the first element to process
        text = np.r_[style_text, text]  # concatenate on 1 axis the prime text + synthesis character sequence
        sequence_prime = np.eye(len(translation), dtype=np.float32)[style_text]
        sequence_prime = np.expand_dims(np.concatenate([sequence_prime, np.zeros((1, len(translation)))]), axis=0)

    sequence = np.eye(len(translation), dtype=np.float32)[text]
    sequence = np.expand_dims(np.concatenate([sequence, np.zeros((1, len(translation)))]), axis=0)

    phi_data, window_data, kappa_data, stroke_data = [], [], [], []
    sess.run(vs.zero_states)
    sequence_len = len(args_text) + style_len
    for s in range(1, 60 * sequence_len + 1):
        is_priming = s < prime_len

        # print('\r[{:5d}] sampling... {}'.format(s, 'priming' if is_priming else 'synthesis'), end='')

        e, pi, mu1, mu2, std1, std2, rho, \
        finish, phi, window, kappa = sess.run([vs.e, vs.pi, vs.mu1, vs.mu2,
                                               vs.std1, vs.std2, vs.rho, vs.finish,
                                               vs.phi, vs.window, vs.kappa],
                                              feed_dict={
                                                  vs.coordinates: coord[None, None, ...],
                                                  vs.sequence: sequence_prime if is_priming else sequence,
                                                  vs.bias: args.bias
                                              })

        if is_priming:
            # Use the real coordinate if priming
            coord = prime_coords[s]
        else:
            # Synthesis mode
            phi_data += [phi[0, :]]
            window_data += [window[0, :]]
            kappa_data += [kappa[0, :]]
            # ---
            g = np.random.choice(np.arange(pi.shape[1]), p=pi[0])
            coord = sample(e[0, 0], mu1[0, g], mu2[0, g],
                           std1[0, g], std2[0, g], rho[0, g])
            coords += [coord]
            stroke_data += [[mu1[0, g], mu2[0, g], std1[0, g], std2[0, g], rho[0, g], coord[2]]]

            if not args.force and finish[0, 0] > 0.8:
                # print('\nFinished sampling!\n')
                break

    coords = np.array(coords)
    coords[-1, 2] = 1.

    return phi_data, window_data, kappa_data, stroke_data, coords


def main():
    with open(os.path.join('data', 'translation.pkl'), 'rb') as file:
        translation = pickle.load(file)
    rev_translation = {v: k for k, v in translation.items()}
    charset = [rev_translation[i] for i in range(len(rev_translation))]
    charset[0] = ''

    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.2)
    config = tf.ConfigProto(
        device_count={'GPU': 1},
        gpu_options=gpu_options
    )

    words = []
    with open('google-10000-english-usa.txt') as f:
        for l in f:
            words.append(l.strip())

    with tf.Session(config=config) as sess:
        saver = tf.train.import_meta_graph(args.model_path + '.meta')
        saver.restore(sess, args.model_path)

        style = None
        if args.style is not None:
            with open(os.path.join('data', 'styles.pkl'), 'rb') as file:
                styles = pickle.load(file)

            if args.style > len(styles[0]):
                raise ValueError('Requested style is not in style list')

            style = [styles[0][args.style], styles[1][args.style]]

        data_dir = 'gen'
        gt_dir = 'gt'
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        if not os.path.isdir(gt_dir):
            os.makedirs(gt_dir)

        idx = 0
        record_file = '{}/{}.txt'.format(gt_dir, uuid.uuid4())

        def write_record(record_list):
            with open(record_file, 'a') as res:
                for idx, word in record:
                    res.write('{},{}\n'.format(idx, word))
            del record_list[:]

        record = []
        size = args.size
        with tqdm(total=size) as pbar:
            while idx < size:
                w1, w2 = random.choice(words), random.choice(words)
                if len(w1) <= 1 or len(w2) <= 1:
                    continue
                args_text = '{} {}.'.format(w1, w2)

                phi_data, window_data, kappa_data, stroke_data, coords = sample_text(sess, args_text, translation,
                                                                                     style)
                strokes = np.array(stroke_data)
                strokes[:, :2] = np.cumsum(strokes[:, :2], axis=0)

                fig, ax = plt.subplots(1, 1)
                for stroke in split_strokes(cumsum(np.array(coords))):
                    plt.plot(stroke[:, 0], -stroke[:, 1])
                # ax.set_title('Handwriting')
                ax.set_aspect('equal')
                ax.set_axis_off()
                id_ = uuid.uuid4()
                plt.savefig('{}/{}.png'.format(data_dir, id_), bbox_inches='tight', pad_inches=0)
                # plt.show()
                plt.close(fig)
                record.append((id_, args_text))
                idx += 1
                pbar.update(1)

                if idx % 10 == 0:
                    write_record(record)
        write_record(record)


if __name__ == '__main__':
    main()
