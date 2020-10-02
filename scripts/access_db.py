"""
==========
Access DB
==========

Access the experiments saved on mongoDB from the command line:

>>> python -m scripts.access_db
"""

import argparse
import datetime
import json

from pymongo import MongoClient
from vivarium.core.emitter import (
    data_from_database,
    data_to_database,
    DatabaseEmitter,
)
from vivarium.core.experiment import timestamp
from vivarium.core.process import serialize_value


def ask_confirm(msg='Are you sure?'):
    answer = ''
    while answer not in ('yes', 'no'):
        answer = input(msg + ' [yes/no] ')
    return True if answer == 'yes' else False


def id_in_db(experiment_id, db):
        query = {'experiment_id': experiment_id}
        existing_config = db.configuration.count_documents(
            query, limit=1
        )
        existing_history = db.history.count_documents(
            query, limit=1
        )
        existing = existing_config + existing_history
        return existing != 0


class AccessDB(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='access experiments from database')
        parser = self.add_arguments(parser)
        self.args = parser.parse_args()

        # mongo client
        config = {
            'host': '{}:{}'.format(self.args.host, self.args.port),
            'database': self.args.database_name
        }
        emitter = DatabaseEmitter(config)
        self.db = emitter.db

        # history collection from this db
        self.history = getattr(self.db, 'history')

    def print_info(self, experiment_id):
        data = self.db.configuration.find(
            {'experiment_id': experiment_id},
            {'name': 1, 'description': 1, 'time_created': 1})
        name = data[0]['name']
        description = data[0]['description']
        time_created = data[0]['time_created']
        date, time = time_created.split('.')

        # get run duration
        time_data = self.history.find({'experiment_id': experiment_id}, {'time': 1})
        time_data = list(time_data)
        last_emit = time_data[-1]['time']

        print(
            'id: {}\n '
            'experiment name: {}\n '
            'time created: {} at {}\n'
            'simulated run time: {}\n'
            'description: {}\n'.format(
                experiment_id,
                name,
                date[4:6] + '/' + date[6:8] + '/' + date[0:4],
                time[0:2] + ':' + time[2:4] + ':' + time[4:6],
                last_emit,
                description)
        )

    def list(self, args):
        experiment_ids = self.db.configuration.distinct('experiment_id')
        print('experiment ids: {}'.format(experiment_ids))

    def info(self, args):
        if len(self.args.experiment_id) == 0:
            experiment_ids = self.db.configuration.distinct('experiment_id')
            for exp_id in experiment_ids:
                self.print_info(exp_id)
        else:
            for exp_id in self.args.experiment_id:
                self.print_info(exp_id)

    def delete(self, args):
        if ask_confirm('Are you sure you want to delete?'):
            for delete in self.args.experiment_id:
                query = {'experiment_id': delete}
                self.db.history.delete_many(query)
                self.db.configuration.delete_many(query)

    def download(self, args):
        for experiment_id in args.experiment_id:
            data, environment_config = data_from_database(
                experiment_id, self.db)
            downloaded = {
                'data': data,
                'environment_config': environment_config,
            }
            serialized = serialize_value(downloaded)
            with open('{}.json'.format(experiment_id), 'w') as f:
                json.dump(serialized, f)

    def upload(self, args):
        for filepath in args.json_file:
            with open(filepath, 'r') as f:
                downloaded = json.load(f)
            data = downloaded['data']
            environment_config = downloaded['environment_config']
            experiment_id = environment_config['experiment_id']
            if id_in_db(experiment_id, self.db):
                print(
                    'FAILED: Database contains experiment ID {}'.format(
                        experiment_id)
                )
                return
            data_to_database(data, environment_config, self.db)


    def access(self):
        # Each subcommand parser uses set_defaults to set the `func` arg
        # to the function that handles that subcommand. Therefore, we
        # can call the correct subcommand parser by calling
        # self.args.func.
        func = self.args.func(self.args)

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--host',
            default='localhost',
            type=str,
            help=(
                'Host at which to access local mongoDB instance. '
                'Defaults to "localhost".'))
        parser.add_argument(
            '-p', '--port',
            default=27017,
            type=int,
            help=(
                'Port at which to access local mongoDB instance. '
                'Defaults to "27017".'))
        parser.add_argument(
            '-b', '--database_name',
            default='simulations',
            type=str,
            help=(
                'Name of database on local mongoDB instance to read from. '
                'Defaults to "simulations".'))

        subparsers = parser.add_subparsers()

        parser_list = subparsers.add_parser(
            'list', description='List all experiment IDs in database.')
        parser_list.set_defaults(func=self.list)

        parser_delete = subparsers.add_parser(
            'delete', description='Delete experiments from database.')
        parser_delete.add_argument(
            'experiment_id',
            nargs='+',
            default=False,
            type=str,
            help='List of experiment IDs to delete.',
        )
        parser_delete.set_defaults(func=self.delete)

        parser_info = subparsers.add_parser(
            'info', description='Get info on a list of experiment IDs.')
        parser_info.add_argument(
            'experiment_id',
            nargs='+',
            type=str,
            default=False,
            help=(
                'Get info on a list of experiment ids. '
                'if no arguments provided, displays all experiment info'))
        parser_info.set_defaults(func=self.info)

        parser_download = subparsers.add_parser(
            'download',
            description='Download experiment data as JSON files',
        )
        parser_download.add_argument(
            'experiment_id',
            nargs='+',
            type=str,
            help='IDs of experiment to download.',
        )
        parser_download.set_defaults(func=self.download)

        parser_upload = subparsers.add_parser(
            'upload',
            description='Upload experiment data from JSON files.',
        )
        parser_upload.add_argument(
            'json_file',
            nargs='+',
            type=str,
            help='JSON file with experiment data to upload.',
        )
        parser_upload.set_defaults(func=self.upload)

        return parser


if __name__ == '__main__':
    access = AccessDB()
    access.access()
