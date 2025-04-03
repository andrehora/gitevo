import argparse
from gitevo import GitEvo
from gitevo.cli_reports import report_mappings


OK, ERR = 0, 1

def parse_args(args=None):

    parser = argparse.ArgumentParser(description='Command line for GitEvo')

    parser.add_argument(
        'repo',
        type=str,
        help='Git repository to be analyzed. It can be a remote Git repository or a path a local Git repository.'
    )

    parser.add_argument(
        '-r',
        '--report-type',
        default='python',
        choices=['python', 'js', 'ts', 'java', 'fastapi'],
        type=str,
        help='Report type to be generated. Default is python.'
    )

    parser.add_argument(
        '-f',
        '--from-year',
        type=int,
        help='Filter commits to be analyzed (from year).'
    )

    parser.add_argument(
        '-t',
        '--to-year',
        type=int,
        help='Filter commits to be analyzed (to year).'
    )

    parser.add_argument(
        '-m',
        '--month',
        action='store_true',
        help='Set to analyze commits by month.'
    )

    parser.add_argument(
        '-l',
        '--last-version-only',
        action='store_true',
        help='Set to analyze the last version only.'
    )

    return parser.parse_args(args)


class GitEvoCLI:

    def __init__(self, args=None):

        parsed_args = parse_args(args)

        self.repo = parsed_args.repo
        self.report_type = parsed_args.report_type
        self.from_year = parsed_args.from_year
        self.to_year = parsed_args.to_year
        
        self.date_unit = 'year'
        if parsed_args.month:
            self.date_unit = 'month'

        self.last_version_only = False
        if parsed_args.last_version_only:
            self.last_version_only = True
        

    def run(self):

        report = report_mappings.get(self.report_type)
        evo = GitEvo(repo=self.repo, extension=report.extension, from_year=self.from_year, 
                     to_year=self.to_year, date_unit=self.date_unit, last_version_only=self.last_version_only)
        report.metrics(evo)
        evo.run()
        return OK

def main(args=None):
    try:
        status = GitEvoCLI(args).run()
    except Exception as e:
        print(e)
        status = ERR
    return status