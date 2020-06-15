# -*- coding: utf-8 -*-
import tensorflow as tf

from core.metrics import COCOeval
from core.callbacks.utils import local_eval


class COCOEvalCheckpoint(tf.keras.callbacks.Callback):

    def __init__(self,
                 save_path,
                 eval_model,
                 model_cfg,
                 eval_n_samples=None,
                 eval_per_batch=1000,
                 only_save_weight=True,
                 verbose=0):
        super(COCOEvalCheckpoint, self).__init__()
        self.save_path = save_path
        self.eval_model = eval_model
        self.model_cfg = model_cfg

        self.only_save_weight = only_save_weight
        self.verbose = verbose
        self.eval_n_samples = eval_n_samples
        self.eval_per_batch = eval_per_batch

        self._image_size = self.model_cfg['test']['image_size'][0]
        self._best_AP = -float('inf')

        self.name_path = self.model_cfg['train']['name_path']
        self.test_path = self.model_cfg['test']['anno_path']

    def on_batch_end(self, batch, logs=None):
        if batch % self.eval_per_batch != self.eval_per_batch - 1:
            return

        print('\nTest')
        AP = local_eval(COCOeval, self.eval_model, self._image_size, self.test_path, self.name_path, self.eval_n_samples, self.verbose)

        if AP > self._best_AP:
            if self.save_path is None:
                if self.verbose > 0:
                    print("AP improved from {:.2%} to {:.2%}".format(self._best_AP, AP))
            else:
                save_path = self.save_path.format(mAP=AP)
                if self.verbose > 0:
                    print(
                        "AP improved from {:.2%} to {:.2%}, saving model to {}".format(self._best_AP, AP, save_path))
                if self.only_save_weight:
                    self.eval_model.save_weights(save_path)
                else:
                    self.eval_model.save(save_path)
            self._best_AP = AP
        else:
            if self.verbose > 0:
                print("AP not improved from {:.2%}".format(self._best_AP))

    # def on_epoch_end(self, epoch, logs=None):
    #
    #     if epoch % self.sample_rate != self.sample_rate - 1:
    #         return
    #
    #     print('\nTest')
    #     AP = local_eval(COCOeval, self.eval_model, self._image_size, self.test_path, self.name_path, self.verbose)
    #
    #     if AP > self._best_AP:
    #         if self.save_path is None:
    #             if self.verbose > 0:
    #                 print("AP improved from {:.2%} to {:.2%}".format(self._best_AP, AP))
    #         else:
    #             save_path = self.save_path.format(mAP=AP)
    #             if self.verbose > 0:
    #                 print(
    #                     "AP improved from {:.2%} to {:.2%}, saving model to {}".format(self._best_AP, AP, save_path))
    #             if self.only_save_weight:
    #                 self.eval_model.save_weights(save_path)
    #             else:
    #                 self.eval_model.save(save_path)
    #         self._best_AP = AP
    #     else:
    #         if self.verbose > 0:
    #             print("AP not improved from {:.2%}".format(self._best_AP))
