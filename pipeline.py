import sys
import os, json
import pickle
from argparse import Namespace
import backend_utils
# import cv2

BASE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(os.path.join(BASE, 'pose/analysis'))
sys.path.append(os.path.join(BASE, 'pose/analysis/utils'))
sys.path.append(os.path.join(BASE, 'classification/tsc/utils'))


def run_video_detection(vid, leg):
    from analyse_vid_light import start as start_detection

    vid_args = Namespace()
    vid_args.video_path = vid
    vid_args.pose_config = os.path.join(BASE, 'pose/mmpose-files/hrnet_w32_coco_wholebody_256x192_dark.py')
    vid_args.pose_checkpoint = os.path.join(BASE, 'pose/mmpose-files/hrnet_w32_coco_wholebody_256x192_dark-469327ef_20200922.pth')
    vid_args.folder_box = os.path.join(BASE, 'pose/mmdet-files')
    vid_args.show = False
    vid_args.device = 'cpu'
    vid_args.box_thr = 0.1
    vid_args.kpt_thr = 0.1
    vid_args.save_pixels = False
    vid_args.skip_rate = 1
    vid_args.flip = leg == 'L'
    vid_args.save_vid = False

    print(vid_args.pose_checkpoint)
    poses, meta, fp = start_detection(vid_args)
    del start_detection
    print(fp)
    return poses, meta['fps']


def extract_reps(data, fps):
    from extract_reps import main as get_datasets

    rep_args = Namespace()
    rep_args.filepath = ''
    rep_args.debug = False
    rep_args.rate = 25
    rep_args.save_numpy = False

    return get_datasets(rep_args, data, fps)

def assess_subject(datasets, datasets100):
    from eval_vid import main as main_asses

    return main_asses(Namespace(), datasets, datasets100, BASE)

# def pipe(vid, id, leg, attempt, file, debug):
def pipe(file_path, leg, debug):
    print(id)
    open('ONGOING', 'w').close()
    # s3_base = os.path.dirname(vid)
    # local_vid_path = 'vid.' + vid.split('.')[-1]
    local_vid_path = os.path.join('/data', file_path)

    if debug is None:
        # downloaded = backend_utils.download_from_aws(local_vid_path, vid)

        # if downloaded:
        poses, fps = run_video_detection(local_vid_path, leg)
        # os.remove(local_vid_path)
        print('keypoints found')

        datasets, datasets100 = extract_reps(poses, fps)
        print('datasets found')
        # with open('/data/datasets.pkl', 'wb') as fo:
        #     pickle.dump({'data': datasets, 'data100': datasets100}, fo)
        # with open('/data/datasets.pkl', 'rb') as fi:
        #     d = pickle.load(fi)
        #     datasets = d['data']
        #     datasets100 = d['data100']
        # print('data saved')
        print('deleting functions...')
        # del poses
        # del extract_reps
        
        results = assess_subject(datasets, datasets100)
        print('results found')
        with open(f"{local_vid_path.split('.')[0]}.json", 'w') as fo:
            json.dump(results, fo)
      
def pipe_debug(vid, id, leg):
    import pickle
    f = open(os.path.join(BASE, 'inference/datadebug/data.pkl'), 'rb')
    datasets = pickle.load(f)
    f.close()
    f = open(os.path.join(BASE, 'inference/datadebug/data100.pkl'), 'rb')
    datasets100 = pickle.load(f)
    f.close()

    del pickle, f

    from eval_vid import main as assess_subject
    results = assess_subject(Namespace(), datasets=datasets,
                             datasets100=datasets100,
                             base_path=BASE)

    print(results)


if __name__ == '__main__':
    print('starting...')
    out = 'out3'
    pipe(out)
