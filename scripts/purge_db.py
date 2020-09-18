from pymongo import MongoClient
import argparse

class Purge(object):

    def __init__(self):
        type = 'database'
        url = 'localhost:27017'
        database = 'simulations'

        parser = argparse.ArgumentParser(description='purge experiments from database')
        parser = self.add_arguments(parser)
        args = parser.parse_args()
        self.experiments = args.experiments

        self.client = MongoClient(url)
        self.db = getattr(self.client, database)

        if args.get:
            experiment_ids = self.db.configuration.distinct('experiment_id')
            print('experiment ids: {}'.format(experiment_ids))


    def purge(self):
        # delete database entries
        if self.experiments == 'None':
            print('provide experiment_ids to delete with -e exp_id. to delete all -e all')
        elif self.experiments == 'all':
            query = {}
            self.db.history.delete_many(query)
            self.db.configuration.delete_many(query)
        else:
            for experiment in self.experiments:
                query = {'experiment_id': experiment}
                self.db.history.delete_many(query)
                self.db.configuration.delete_many(query)

    def add_arguments(self, parser):
        parser.add_argument(
            '-e', '--experiments',
            nargs='+',
            type=str,
            default='None',
            help='which experiments to purge')

        parser.add_argument(
            '-g', '--get',
            action='store_true',
            default=False,
            help='get all experiment ids in db')

        return parser

if __name__ == '__main__':
    purge = Purge()
    purge.purge()
