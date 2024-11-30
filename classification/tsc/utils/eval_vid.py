from argparse import ArgumentParser, ArgumentTypeError
import os
import numpy as np
print('np imported')
from tensorflow.keras import models as keras_models
print('tf imported')
import coral_ordinal as coral
print('coral imported')
from confusion_utils import ConfusionCrossEntropy
print('after import')


def main(args, datasets=None, datasets100=None, base_path=''):
    print('before import')
    # import tensorflow.keras as keras
    
    # import numpy as np
    # print('np imported')
    # import coral_ordinal as coral
    # print('coral imported')
    # from confusion_utils import ConfusionCrossEntropy
    # print('after import')
    # from tensorflow.keras import models as keras_models
    print('keras imported')
    poes = ['femval', 'trunk', 'hip', 'kmfp', 'fms']
    results = {}
    for poe in poes:
        # model_path = '/home/filipkr/Documents/xjob/training/ensembles'
        model_path = os.path.join(base_path, f'models/{poe}_aug')
        if datasets is None or datasets100 is None:
            x = np.load(os.path.join(args.root, poe + '.npy'))
            x100 = np.load(os.path.join(args.root, poe + '-100.npy'))
        else:
            x = datasets[poe]
            x100 = datasets100[poe]

        if poe == 'femval':
            # lit = 'Olga-Tokarczuk'
            models = ['coral-1', 'conf-0', 'conf-1', 'conf-2']
            weights = np.array([[0.6,0.6,1],[0.4,0,0], [0,0.4,0],[0,0,0.1]])
            # models = ['coral-100-7000', 'xx-coral-100-7000',
            #           'xx-conf-100-7000', 'xx-conf-100-11000', 'xx-conf-9000']
            # weights = np.array([[1/3, 1.25/3, 1/3], [1/3, 1.25/3, 1/3],
            #                     [1/3, 0, 0], [0, 0, 1/3], [0, 1.25/3, 0]])
            
        elif poe == 'hip':
            # lit = 'Sigrid-Undset'
            models = ['coral-1', 'conf-0', 'conf-100-1', 'conf-100-2']
            weights = np.array([[0.5,0.5,0.6], [0.5, 0, 0], [0, 0.5, 0], [0,0,0.5]])
            # models = ['coral-100-13000', 'coral-13000', 'conf-100-10000',
            #           'conf-10001', 'xx-coral-100-10003']
            # weights = np.array([[1/4, 1.05/4, 1.5/4], [1/4, 1.05/4, 1.5/4],
            #                     [1/2, 0, 0], [0, 1.05/2, 0], [0, 0, 1.5/2]])
        elif poe == 'kmfp':
            # lit = 'Mikhail-Sholokhov'
            models = ['coral-1', 'conf-0', 'conf-2']
            weights = np.array([[0.6,1.1,0.9], [0.4,0,0], [0,0,0.3]])
            # models = ['inception-3010', 'xx-inception-3010', 'xx-conf-3010',
            #           'conf-100-13000', 'xx-conf-3025']
            # weights = np.array([[1/3, 1.25*1/3, 1.25/3],
            #                     [1/3, 1.25*1/3, 1.25/3], [1/3, 0, 0],
            #                     [0, 1.25*1/3, 0], [0, 0, 1.25/3]])
        elif poe == 'trunk':
            # lit = 'Isaac-Bashevis-Singer'
            models = ['coral-1', 'conf-0', 'conf-100-1', 'conf-2']
            weights = np.array([[0.5,0.5,0.5], [0.5,0,0],[0,0.5,0],[0,0,0.5]])
            # models = ['coral-100-11', 'coral-100-10', 'xx-conf-100-11',
            #           'conf-15', 'xx-coral-100-10']
            # weights = np.array([[1/3, 1.15/3, 1/3], [1/3, 1.15/3, 1/3],
            #                     [1/3, 0, 0], [0, 1.15/3, 0], [0, 0, 1/3]])
        elif poe == 'fms':
            models = ['coral-1', 'conf-0', 'conf-100-1']
            weights = np.array([[0.6,0.6,1.1], [0.4,0,0], [0,0.4,0]])

        # model_path = os.path.join(model_path, lit + '10')
        ensembles = [os.path.join(model_path, i) for i in models]
        paths = [os.path.join(root, 'model_fold_1.hdf5') for root in ensembles]
        all_probs = np.zeros((len(models), x.shape[0], 3))

        for model_i, model_path in enumerate(paths):
            # print(model_path)
            input = x100 if '-100-' in model_path else x
            model = keras_models.load_model(model_path, custom_objects={
                                            'CoralOrdinal': coral.CoralOrdinal,
                                            'OrdinalCrossEntropy':
                                            coral.OrdinalCrossEntropy,
                                            'MeanAbsoluteErrorLabels':
                                            coral.MeanAbsoluteErrorLabels,
                                            'ConfusionCrossEntropy':
                                            ConfusionCrossEntropy})

            # print(model.summary())
            # print(input.shape)
            # print(lit)
            print(poe)
            result = model.predict(input)
            # print(model.summary())
            # print(model_path)
            # print(input.shape)
            # print(result.shape)
            del model
            probs = coral.ordinal_softmax(
                result).numpy() if 'coral' in model_path else result
            # probs = result
            # print(probs.shape)
            # print(weights[model_i, ...].shape)
            # print(result)
            # print(probs)
            probs = probs * weights[model_i, ...]
            # print(probs)

            all_probs[model_i, ...] = probs

        ensemble_probs = np.sum(all_probs, axis=0)
        # print(ensemble_probs)
        # threshold
        ensemble_probs = (ensemble_probs > 0.2) * ensemble_probs
        # print(ensemble_probs)
        # ev fel shape ....
        summed = np.mean(ensemble_probs, axis=0)
        print('RESULT')
        print(summed)
        # print()
        pred_combined = int(np.argmax(np.mean(ensemble_probs, axis=0)))
        # pred = np.argmax(pred_subj, axis=1)

        print('\n')
        print(f'Prediction for POE, {poe}: {pred_combined}')
        print(f'Certainties: {np.mean(ensemble_probs, axis=0)}')
        print(f'Summed-score: {summed}')

        print(ensemble_probs)
        res = {'pred': pred_combined, 'conf': summed.tolist(),
               'detailed': ensemble_probs.tolist()}
        results[poe] = res

    return results


def str2bool(v):
    ''' pass bool wtih argparse'''
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root', default='')
    # parser.add_argument('data')
    args = parser.parse_args()
    main(args)
