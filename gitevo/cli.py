import argparse

from importlib.metadata import version

from gitevo import GitEvo
from gitevo.reports import report_mappings


OK, ERR = 0, 1

def parse_args(args=None):

    parser = argparse.ArgumentParser(description='Command line for GitEvo')

    parser.add_argument(
        'git_repo',
        type=str,
        help='Git repository to analyze. Accepts a Git URL, a local Git repository, or a directory containing multiple Git repositories. Example: gitevo https://github.com/pallets/flask'
    )

    parser.add_argument(
        '-r',
        '--report',
        default='python',
        choices=report_mappings.keys(),
        type=str,
        help='Report to be generated. Default is python.'
    )

    parser.add_argument(
        '-f',
        '--from-year',
        type=int,
        help='Filter commits to be analyzed (from year). Default is last five years.'
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
        '-v',
        '--version',
        action='version',
        version=gitevo_version(),
        help='Show the GitEvo version.'
    )

    return parser.parse_args(args)

def gitevo_version():
    try:
        v = version("gitevo")
        return f'GitEvo {v}'
    except Exception:
        return 'GitEvo dev'

class GitEvoCLI:

    def __init__(self, args=None):

        parsed_args = parse_args(args)

        self.git_repo = parsed_args.git_repo
        self.report = parsed_args.report
        self.from_year = parsed_args.from_year
        self.to_year = parsed_args.to_year
        
        self.date_unit = 'year'
        if parsed_args.month:
            self.date_unit = 'month'

    def run(self):

        report = report_mappings.get(self.report)
        evo = GitEvo(repo=self.git_repo,
                     extension=report.extension,
                     from_year=self.from_year,
                     to_year=self.to_year,
                     date_unit=self.date_unit)
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