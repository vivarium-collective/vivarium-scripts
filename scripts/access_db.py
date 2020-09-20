from pymongo import MongoClient
import argparse

class AccessDB(object):

    def __init__(self):
        type = 'database'
        url = 'localhost:27017'
        database = 'simulations'

        parser = argparse.ArgumentParser(description='purge experiments from database')
        parser = self.add_arguments(parser)
        self.args = parser.parse_args()

        self.client = MongoClient(url)
        self.db = getattr(self.client, database)

    def print_info(self, experiment_id):
        data = self.db.configuration.find(
            {'experiment_id': experiment_id},
            {'name': 1, 'description': 1, 'time_created': 1})
        name = data[0]['name']
        description = data[0]['description']
        time_created = data[0]['time_created']
        date, time = time_created.split('.')
        print(
            'id: {}\n '
            'experiment name: {}\n '
            'time created: {} at {}\n'
            'description: {}\n'.format(
                experiment_id,
                name,
                date[4:6] + '/' + date[6:8] + '/' + date[0:4],
                time[0:2] + ':' + time[2:4] + ':' + time[4:6],
                description)
        )

    def access(self):

        if self.args.list:
            experiment_ids = self.db.configuration.distinct('experiment_id')
            print('experiment ids: {}'.format(experiment_ids))

        if self.args.info:
            for exp_id in self.args.info:
                self.print_info(exp_id)

        if self.args.delete:
            for delete in self.args.delete:
                query = {'experiment_id': delete}
                self.db.history.delete_many(query)
                self.db.configuration.delete_many(query)

        if self.args.view:
            experiment_ids = self.db.configuration.distinct('experiment_id')
            for exp_id in experiment_ids:
                self.print_info(exp_id)


    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--delete',
            nargs='+',
            type=str,
            default='None',
            help='provide list of experiment ids to delete')

        parser.add_argument(
            '-i', '--info',
            nargs='+',
            type=str,
            default=False,
            help='get info on a list of experiment ids')

        parser.add_argument(
            '-l', '--list',
            action='store_true',
            default=False,
            help='get list of all experiment ids in db')

        parser.add_argument(
            '-v', '--view',
            action='store_true',
            default=False,
            help='get all experiment ids in db')

        return parser

if __name__ == '__main__':
    access = AccessDB()
    access.access()