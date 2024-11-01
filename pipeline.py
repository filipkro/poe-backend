import sys
import os, json
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


# def pipe(vid, id, leg, attempt, file, debug):
def pipe(file_path, leg, debug):
    print(id)
    open('ONGOING', 'w').close()
    # s3_base = os.path.dirname(vid)
    # local_vid_path = 'vid.' + vid.split('.')[-1]
    local_vid_path = os.path.join('/data', file_path)
    # result = cv2.VideoWriter('filename.avi',  
    #                      cv2.VideoWriter_fourcc(*'MJPG'), 
    #                      10, size) 
    # file.save(local_vid_path)
    # file.close()
    # print('writing file')
    # print(file)
    # with open(local_vid_path, 'wb') as fo:
    #     fo.write(file)
    # print(local_vid_path)
    # local_vid_path = '/app/dummy-data/950203/ATTEMPT1/vid.mts'
    # ONGOING = os.path.join(s3_base, 'ONGOING')


    # uploaded = backend_utils.upload_to_aws('ONGOING', ONGOING)
    if debug is None:
        # downloaded = backend_utils.download_from_aws(local_vid_path, vid)

        # if downloaded:
        poses, fps = run_video_detection(local_vid_path, leg)
        # os.remove(local_vid_path)
        print('keypoints found')
        # all_data = {'poses': poses, 'fps': fps}
        # import pickle  # noqa
        # f = open('poses.pkl', 'wb')
        # pickle.dump(all_data, f)
        # f.close()

        # os.remove('poses.pkl')

        datasets, datasets100 = extract_reps(poses, fps)
        print('datasets found')
        # os.
        # uploaded = backend_utils.upload_to_aws('/app/debug.jpg',
        #                                         os.path.join(s3_base,
        #                                                     'debug.jpg'))
        # if not uploaded:
        #     return "issue connecting S3 when uploading data, aborting..."
        # os.remove('/app/debug.jpg')

        # fp = '/app/data.pkl'
        # fp100 = '/app/data_100.pkl'
        # f = open(fp, 'wb')
        # pickle.dump(datasets, f)
        # f.close()
        # f = open(fp100, 'wb')
        # pickle.dump(datasets100, f)
        # f.close()
        # uploaded = backend_utils.upload_to_aws(fp, os.path.join(s3_base,
        #                                                         'data.pkl'))
        # if not uploaded:
        #     return "issue connecting S3 when uploading data, aborting..."
        # uploaded = backend_utils.upload_to_aws(fp100,
        #                                         os.path.join(s3_base,
        #                                                     'data_100.pkl'))
        # if not uploaded:
        #     return "issue connecting S3 when uploading data, aborting..."

        # os.remove(fp)
        # os.remove(fp100)

        # del f, pickle, fp, fp100

        from eval_vid import main as assess_subject
        results = assess_subject(Namespace(), datasets=datasets,
                                datasets100=datasets100,
                                base_path=BASE)

        with open(f"{local_vid_path.split('.')[0]}.json", 'w') as fo:
            json.dump(results, fo)
        # fp = 'results.pkl'
        # f = open(fp, 'wb')
        # import pickle  # noqa
        # pickle.dump(results, f)
        # f.close()

        # uploaded = backend_utils.upload_to_aws(fp, os.path.join(s3_base,
        #                                                         'results.pkl'))
        # os.remove(fp)
        # if not uploaded:
        #     return "Could not save result to S3"

        # deleted = backend_utils.delete_from_aws(ONGOING)
        # if not deleted:
        #     return "ONGOING flag could not be deleted from S3"


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
