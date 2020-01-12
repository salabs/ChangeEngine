import sys
import json
import argparse
from urllib.request import Request, urlopen

DESCRIPTION = """Use ChangeEngine to generate Robot Framework argument files that
 select a prioritized subset of test cases based on given changes to system
 under test."""

TEST_SELECTOR_TEMPLATE = '--test {}\n'

def get_priority_list(args, changes):
    data = {"context": "default", "changes": changes,
            "tests": {"repository": args.repository, 'subtype': 'Robot Framework'}}
    url = "{}/prioritize/".format(args.change_engine_url)
    request = Request(url)
    request.add_header('Content-Type', 'application/json;')
    body = json.dumps(data)
    response = urlopen(request, body.encode("utf-8"))
    if response.getcode() == 200:
        return json.loads(response.read())['tests']
    else:
        print("ERROR: ChangeEngine request failed. Return code: {}".format(response.getcode()))
        print(response.read())
        exit(1)

def write_argument_files(args, tests):
    prioritized = []
    while len(prioritized) < args.top and tests:
        prioritized.append(tests.pop(0))
    rest = tests

    with open(args.prioritized_file, 'w') as argument_file:
        for test in prioritized:
            argument_file.write(TEST_SELECTOR_TEMPLATE.format(test['name']))
    if args.remnant:
        with open(args.remnant_file, 'w') as argument_file:
            for test in rest:
                argument_file.write(TEST_SELECTOR_TEMPLATE.format(test['name']))

def changes_from_stdin():
    changes = []
    line = input()
    while True:
        changes.append(line)
        try:
            line = input()
        except EOFError:
            break
    return changes

def changes_from_args():
    return sys.argv[1:]


if __name__ == '__main__':
    if sys.version_info[0] < 3:
        sys.exit('Unsupported Python version (' + str(sys.version_info.major) + '). Please use version 3.')
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--change_engine_url', required=True, help='url for the change engine instance')
    parser.add_argument('--repository', default='default repo', help='repository of the tests')
    parser.add_argument('--context', default='default', help='context of the prioritization (defaul: default)')
    parser.add_argument('--prioritized_file', default='prioritized.robot', help='sets the name of the prioritized argument file (default: prioritized.robot)')
    parser.add_argument('--top', type=int, default=3, help='number of tests in the prioritized set (default: 10)')
    parser.add_argument('--remnant', action='store_true', help='generate a remnant argument file that contains the rest of the test cases')
    parser.add_argument('--remnant_file', default='remnant.robot', help='sets the name of the remnant argument file (default: remnant.robot)')
    parser.add_argument('--changes', nargs='+', help='list of changes to the system under test')
    parser.add_argument('--stdin', action='store_true', help='read changes from stdin, items separated by new lines')
    args = parser.parse_args()

    changes = changes_from_stdin() if args.stdin else args.changes
    priority_list = get_priority_list(args, changes)
    write_argument_files(args, priority_list)
