import os
import cv2 #opencv
import numpy as np #numpy
import _init_paths #sets up paths with caffe and test_utils
import cPickle
import demo_test_utils as tutils 
import sys
import time
import json
sys.path.append('/home/ubuntu/caffe-captioning/vision_concepts_linux64/code/caffe/python')
import caffe

def loadModel(prototxt_file, model_file, vocab_file):
    means = np.array([[[ 103.939, 116.779, 123.68]]]);
    base_image_size = 565;
    with open(vocab_file, 'rb') as f:
       vocab = cPickle.load(f)
    model = tutils.load_model(prototxt_file, model_file, base_image_size, means, vocab);
    return model

def testImg(im, model):
    net = model['net'];
    base_image_size = model['base_image_size'];
    means = model['means'];
    sc, mil_prob = tutils.test_img(im, net, base_image_size, means);
    return np.squeeze(mil_prob), np.squeeze(sc); #remove singleton dimensions
	
def printAttribs(sc, imname, model, topK=30):	
	srt_inds = np.argsort(sc)[::-1]; #sort in descending order
	words = model['vocab']['words'];
	print '%s: '%(imname)
	for i in range(topK):
		print '{:s} ({:.2f}), '.format(words[srt_inds[i]], sc[srt_inds[i]]);
	print '\n'


def printWordsWithProb(mil_prob, model, removeFunctional = False):
    functional_words = [];
    if removeFunctional:
        functional_words = ['a', 'on', 'of', 'the', 'in', 'with', 'and', 'is', 'to', 'an', 'two', 'at', 'next', 'are'];
    vocab = model['vocab'];
    words = vocab['words'];
    for i in range(len(words)):
        if words[i] not in functional_words:
            print mil_prob[i], words[i];
        

def loadProcessedTags(video_name):
    MSR_CAPTION_FOLDER = '/mnt/tags/msr-caption'
    msr_data = load_video_msr_caption(MSR_CAPTION_FOLDER, video_name)

    return msr_data 

def loadKeyFrames(video_name):
    KEYFRAME_FOLDER = '/home/t-yuche/gt-labeling/frame-subsample/keyframe-info'
    keyframe_file = os.path.join(KEYFRAME_FOLDER, video_name + '_uniform.json')
    
    with open(keyframe_file) as json_file:
        keyframes = json.load(json_file)

    return keyframes 

if __name__ == "__main__":

    ##
    top_k = 60
    ##
    
    caffe.set_mode_gpu()
    prototxt_file = 'demoData/mil_finetune.prototxt.deploy';
    model_file = 'demoData/snapshot_iter_240000.caffemodel';
    vocab_file = 'demoData/vocab_train.pkl';
    model = loadModel(prototxt_file, model_file, vocab_file);
    periscope_folder = '/home/ubuntu/periscope-playground/videos'
    videos = [x for x in os.listdir(periscope_folder) if x.find('.mp4') >= 0]
    for vid, f in enumerate(videos):

        print vid, len(videos)
        if f.find('.mp4') < 0:
            continue

        video_path = os.path.join(periscope_folder, f)
        outfile = os.path.join('captions', f.split('.')[0] + '.json')
        if os.path.exists(outfile):
            continue
        cap = cv2.VideoCapture(video_path)
        n_frames = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        blob = {}
        blob['imgblobs'] = []
        fid = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if frame == None or frame.size == 0:
                break

            if fid % 30 == 0:
                tic = time.time()
                mil_prob, sc = testImg(frame, model)
                toc = time.time()
                print '(', fid, '/', n_frames, ')', toc - tic
                srt_inds = np.argsort(sc)[::-1]; #sort in descending order
                words = model['vocab']['words'];

                texts = []
                probs  = []  
                for i in range(top_k):
                    texts += [words[srt_inds[i]]]
                    probs += [float(sc[srt_inds[i]])]
                
                img_blob = {}
                img_blob['fid'] = fid
                img_blob['exec_time'] = (toc-tic)
                img_blob['words'] = {'text': texts, 'prob':probs }
                blob['imgblobs'].append(img_blob)

            fid += 1
        cap.release()

        print 'writing predictions to %s...' % (outfile, )
        with open(outfile, 'w') as fh: 
            json.dump(blob, fh)


