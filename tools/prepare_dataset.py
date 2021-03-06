from __future__ import print_function
import sys, os
import argparse
import subprocess
curr_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(curr_path, '..'))
from dataset.pascal_voc import PascalVoc
from dataset.mscoco import Coco
from dataset.kitti import Kitti
from dataset.caltech_pedestrian import CaltechPedestrian
from dataset.caltech_pedestrian_new import CaltechPedestrian_new
from dataset.caltech_pedestrian_new10x import CaltechPedestrian_new10x
from dataset.concat_db import ConcatDB

def load_pascal(image_set, year, devkit_path, shuffle=False):
    """
    wrapper function for loading pascal voc dataset

    Parameters:
    ----------
    image_set : str
        train, trainval...
    year : str
        2007, 2012 or combinations splitted by comma
    devkit_path : str
        root directory of dataset
    shuffle : bool
        whether to shuffle initial list

    Returns:
    ----------
    Imdb
    """
    image_set = [y.strip() for y in image_set.split(',')]
    assert image_set, "No image_set specified"
    year = [y.strip() for y in year.split(',')]
    assert year, "No year specified"

    # make sure (# sets == # years)
    if len(image_set) > 1 and len(year) == 1:
        year = year * len(image_set)
    if len(image_set) == 1 and len(year) > 1:
        image_set = image_set * len(year)
    assert len(image_set) == len(year), "Number of sets and year mismatch"

    imdbs = []
    for s, y in zip(image_set, year):
        imdbs.append(PascalVoc(s, y, devkit_path, shuffle, is_train=True))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def load_coco(image_set, dirname, shuffle=False):
    """
    wrapper function for loading ms coco dataset

    Parameters:
    ----------
    image_set : str
        train2014, val2014, valminusminival2014, minival2014
    dirname: str
        root dir for coco
    shuffle: boolean
        initial shuffle
    """
    anno_files = ['instances_' + y.strip() + '.json' for y in image_set.split(',')]
    assert anno_files, "No image set specified"
    imdbs = []
    for af in anno_files:
        af_path = os.path.join(dirname, 'annotations', af)
        imdbs.append(Coco(af_path, dirname, shuffle=shuffle))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def load_kitti(image_set, kitti_path, suffix='', shuffle=False):
    """
    wrapper function for loading kitti dataset
    """
    image_set = [y.strip() for y in image_set.split(',')]
    assert image_set, "No image_set specified"

    imdbs = []
    for s in image_set:
        imdbs.append(Kitti(s, kitti_path, shuffle, suffix, is_train=True))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def load_caltech(image_set, caltech_path, shuffle=False):
    image_set = [y.strip() for y in image_set.split(',')]
    assert image_set, "No image_set specified"
    imdbs = []
    for s in image_set:
        imdbs.append(CaltechPedestrian(s, caltech_path, shuffle, is_train=True))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def load_caltech_new(image_set, caltech_path, shuffle=False):
    image_set = [y.strip() for y in image_set.split(',')]
    assert image_set, "No image_set specified"
    imdbs = []
    for s in image_set:
        imdbs.append(CaltechPedestrian_new(s, caltech_path, shuffle, is_train=True))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def load_caltech_new10x(image_set, caltech_path, shuffle=False):
    image_set = [y.strip() for y in image_set.split(',')]
    assert image_set, "No image_set specified"
    imdbs = []
    for s in image_set:
        imdbs.append(CaltechPedestrian_new10x(s, caltech_path, shuffle, is_train=True))
    if len(imdbs) > 1:
        return ConcatDB(imdbs, shuffle)
    else:
        return imdbs[0]

def parse_args():
    parser = argparse.ArgumentParser(description='Prepare lists for dataset')
    parser.add_argument('--dataset', dest='dataset', help='dataset to use',
                        default='pascal', type=str)
    parser.add_argument('--year', dest='year', help='which year to use',
                        default='2007,2012', type=str)
    parser.add_argument('--set', dest='set', help='train, val, trainval, test',
                        default='trainval', type=str)
    parser.add_argument('--target', dest='target', help='output list file',
                        default=os.path.join(curr_path, '..', 'train.lst'),
                        type=str)
    parser.add_argument('--root', dest='root_path', help='dataset root path',
                        default=os.path.join(curr_path, '..', 'data', 'VOCdevkit'),
                        type=str)
    parser.add_argument('--shuffle', dest='shuffle', help='shuffle list',
                        type=bool, default=True)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    # customized
    #args.dataset = 'kitti'
    #args.set = 'train_total'
    #args.shuffle = False
    #suffixs = ['', '_central', '_small', '_large', '_small_total', '_large_total']
    #suffix = suffixs[5]
    #args.target = os.path.join(curr_path, '..', 'data', 'kitti',
    #                           'rec', 'car', args.set + suffix + '.lst')
    #args.root_path = os.path.join(curr_path, '..', 'data', 'kitti')

    args.dataset = 'caltech'
    args.set = 'train'
    if args.set == 'train':
        args.shuffle = True
    elif args.set == 'val':
        args.shuffle = False
    args.target = os.path.join(curr_path, '..', 'data', 'caltech-pedestrian-dataset-converter',
                               'rec_all', args.set + '.lst')
    args.root_path = os.path.join(curr_path, '..', 'data', 'caltech-pedestrian-dataset-converter')

    suffix = ""

    if args.dataset == 'pascal':
        db = load_pascal(args.set, args.year, args.root_path, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)
    elif args.dataset == 'coco':
        db = load_coco(args.set, args.root_path, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)
    elif args.dataset == 'kitti':
        db = load_kitti(args.set, args.root_path, suffix, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)
    elif args.dataset == 'caltech':
        db = load_caltech(args.set, args.root_path, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)
    elif args.dataset == 'caltech_new':
        db = load_caltech_new(args.set, args.root_path, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)
    elif args.dataset == 'caltech_new10x':
        db = load_caltech_new10x(args.set, args.root_path, args.shuffle)
        print("saving list to disk...")
        db.save_imglist(args.target, root=args.root_path)


    else:
        raise NotImplementedError("No implementation for dataset: " + args.dataset)

    print("List file {} generated...".format(args.target))

    # indicate anaconda Python
    remote_anaconda_path = '/home/binghao/software/anaconda2/bin'
    subprocess.check_call([os.path.join(remote_anaconda_path, "python"),
        os.path.join(curr_path, "..", "mxnet/tools/im2rec.py"),
        os.path.abspath(args.target), os.path.abspath(args.root_path),
        "--shuffle", str(int(args.shuffle)),
        # "--resize", "375",
        "--pack-label", "1", "--num-thread", "20"])

    print("Record file {} generated...".format(args.target.split('.')[0] + '.rec'))
