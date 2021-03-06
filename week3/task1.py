import sys
sys.path.append('../')
from scipy import ndimage
from utils import createTmpSequence, evaluation, metrics, roc
import os
import shutil
import cv2
import numpy as np

def task1(mog2BG, inputpath, groundTruthImgs, tr_frmStart, tr_frmEnd, te_frmStart, te_frmEnd, choiceOfDataset):

    # Number of cnn for the structuring element
    cnn = 8

    recallList = []
    precisionList = []
    for threshold in range(10,2000,100):
        print "Threshold: ",threshold
        if "2" in cv2.__version__:
            mog2BG = cv2.BackgroundSubtractorMOG2(history=150, varThreshold=MOGthreshold, bShadowDetection=False)
        else:
            mog2BG = cv2.createBackgroundSubtractorMOG2(history=150, varThreshold=MOGthreshold, detectShadows=False)
        # Reset tmp folders
        if 'tmpSequence' in os.listdir('../datasets/'+choiceOfDataset):
            shutil.rmtree('../datasets/'+choiceOfDataset+'/tmpSequence/')
        os.makedirs('../datasets/'+choiceOfDataset+'/tmpSequence')
        shutil.rmtree('week3Results/task1/baseWeek2Results')
        os.makedirs('week3Results/task1/baseWeek2Results')
        # if 'FG_evaluation' in os.listdir('../datasets/'+choiceOfDataset):
        #     shutil.rmtree('task3Results/FG_evaluation/')
        # os.makedirs('task3Results/FG_evaluation')

        createTmpSequence(tr_frmStart, tr_frmEnd, choiceOfDataset)


        # Start reading the sequence
        cap = cv2.VideoCapture('../datasets/'+choiceOfDataset+'/tmpSequence/in%03d.jpg')
        ret, frame = cap.read()

        # Structuring elements with 4 and 8 conn
        if cnn == 4:
            str_elem = np.array([[0,1,0],[1,0,1],[0,1,0]])
        else:
            str_elem = np.ones((3,3))


        frameCounter = tr_frmStart
        # While we have not reached the end of the sequence
        while frame is not None:
            # Show and write frames
            # cv2.imwrite('task2Results/frame/fr'+str(frameCounter)+'.jpg', frame)
            # cv2.imwrite('task2Results/FG/in00'+str(frameCounter)+'.jpg', FG/255)

            # Learn the background
            out = mog2BG.apply(frame, learningRate=0.01)
            # cv2.imwrite('week3Results/task1/baseWeek2Results/fg'+str(frameCounter)+'.jpg', out)

            # Apply Hole-Filling
            out = ndimage.binary_fill_holes(out, str_elem).astype(int)
            # cv2.imwrite('week3Results/task1/holeFilling4/fg'+str(frameCounter)+'.jpg', out*255)
            frameCounter += 1

            # Read next frame
            _, frame = cap.read()

        #############################
        #        EVALUATION         #
        #############################

        allFramesResults = []

        # Reset tmp folders
        shutil.rmtree('../datasets/'+choiceOfDataset+'/tmpSequence/')
        os.makedirs('../datasets/'+choiceOfDataset+'/tmpSequence')
        shutil.rmtree('week3Results/task1/FG_evaluation')
        os.makedirs('week3Results/task1/FG_evaluation')
        shutil.rmtree('week3Results/task1/FG_baselineWeek2_evaluation')
        os.makedirs('week3Results/task1/FG_baselineWeek2_evaluation')
        shutil.rmtree('week3Results/task1/holeFilling4')
        os.makedirs('week3Results/task1/holeFilling4')
        shutil.rmtree('week3Results/task1/holeFilling8')
        os.makedirs('week3Results/task1/holeFilling8')


        createTmpSequence(te_frmStart, te_frmEnd, choiceOfDataset)

        cap = cv2.VideoCapture('../datasets/'+choiceOfDataset+'/tmpSequence/in%03d.jpg')
        _, frame = cap.read()

        # While we have not reached the end of the sequence
        while frame is not None:

            # Learn the background
            out = mog2BG.apply(frame, learningRate=0.01)
            # baselineOut = cv2.threshold(out, 50, 255, cv2.THRESH_BINARY)[1]
            # Last week's best results
            # cv2.imwrite('week3Results/task1/FG_baselineWeek2_evaluation/in00'+str(frameCounter)+'.jpg', baselineOut)
            out = ndimage.binary_fill_holes(out, str_elem).astype(int)
            # Hole-filled images
            cv2.imwrite('week3Results/task1/FG_evaluation/in00'+str(frameCounter)+'.jpg', out)
            frameCounter += 1

            # Read next frame
            _, frame = cap.read()


        # CHANGE NEXT LINE TO sequencePath = 'week3Results/task1/FG_baselineWeek2_evaluation/' if you want to evaluate last week's best results
        sequencePath = 'week3Results/task1/FG_evaluation/'
        imgNames = os.listdir(sequencePath)
        imgNames.sort()
        for name in imgNames:
            allFramesResults.append(cv2.cvtColor(cv2.imread(sequencePath+name), cv2.COLOR_BGR2GRAY))
        allFramesResults = np.asarray(allFramesResults)

        metric = []
        TestTP = []
        TestFN = []
        TestTotalFG = []
        TP_res=0
        TN_res=0
        FP_res=0
        FN_res=0

        for idx, img in enumerate(groundTruthImgs):
            pred_labels = allFramesResults[idx]
            true_labels = groundTruthImgs[idx,:,:]
            TP, TN, FP, FN = evaluation(pred_labels,true_labels)
            TestTP.append(TP)
            TP_res+=TP
            TN_res+=TN
            FP_res+=FP
            FN_res+=FN
            TestTotalFG.append(TP+FN)
            metric.append(metrics(TP, TN, FP, FN))
        recall, prec, f1 = metrics(TP_res, TN_res, FP_res, FN_res)

        print "\nMOG2: results for "+choiceOfDataset+"\n\n Recall \t\t Precision \t\t F1\n", " %.3f" % recall, "\t\t\t", " %.3f" % prec, "\t\t\t", " %.3f" % f1

        recallList.append(recall)
        precisionList.append(prec)
        # Reset tmp folder
        shutil.rmtree('../datasets/'+choiceOfDataset+'/tmpSequence/')
        os.makedirs('../datasets/'+choiceOfDataset+'/tmpSequence')

    roc(recallList, precisionList, 'ROC for MOG2')
