from comet_ml import Experiment
import torch

from src.dataset import MCDataset
from src.model import GAE
from src.train import Trainer
from src.utils import calc_rmse, ster_uniform, random_init, init_xavier, init_uniform


def main(params, comet=False):
    if comet:
        experiment = Experiment(api_key="xK18bJy5xiPuPf9Dptr43ZuMk",
                        project_name="gcmc-ml100k", workspace="tanimutomo")
        experiment.log_parameters(params)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dataset = MCDataset(params['root'], params['dataset_name'])
    data = dataset[0].to(device)

    model = GAE(
        dataset.num_nodes,
        params['hidden_size'][0],
        params['hidden_size'][1],
        params['num_basis'],
        dataset.num_relations,
        int(data.num_users),
        params['drop_prob'],
        random_init,
        # ster_uniform,
        params['accum'],
        params['rgc_bn'],
        params['rgc_relu'],
        params['dense_bn'],
        params['dense_relu'],
        params['bidec_drop']
        ).to(device)
    
    model.apply(init_xavier)

    if comet:
        trainer = Trainer(model, dataset, data, calc_rmse, params['epochs'],
                params['lr'], params['weight_decay'], experiment)
    else:
        trainer = Trainer(model, dataset, data, calc_rmse,
                params['epochs'], params['lr'], params['weight_decay'])
    trainer.iterate()


if __name__ == '__main__':
    params = {
            'epochs': 1000,
            'lr': 0.01,
            'weight_decay': 0,
            'drop_prob': 0.7,
            'accum': 'split_stack',
            'rgc_bn': True,
            'rgc_relu': True,
            'dense_bn': True,
            'dense_relu': True,
            'bidec_drop': False,

            'hidden_size': [500, 75],
            'num_basis': 2,

            'root': 'data/ml-100k',
            'dataset_name': 'ml-100k'
            }
    # main(params, comet=True)
    main(params)

