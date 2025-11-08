import argparse
import os
import sys
from collections import Counter
from pathlib import Path
from typing import OrderedDict

if sys.stdout.isatty():
	GREEN = '\033[32m'
	GREY = '\033[90m'
	RESET = '\033[0m'
	YELLOW = '\033[33m'
else:
	GREEN = GREY = RESET = YELLOW = ''

sys.stdout.reconfigure(encoding='utf-8')

GLYPH_FILE = Path(os.path.dirname(__file__)) / 'glyphs.txt'


def load_lines(path: Path) -> list[str]:
	try:
		with open(path, 'r', encoding='utf-8') as f:
			return f.readlines()
	except FileNotFoundError:
		print(f'File not found: {path}', file=sys.stderr)
		sys.exit(2)


def find_all_occurrences(lines: list[str], ch: str) -> list[tuple[int, int, str, int]]:
	occ = []
	for i, raw in enumerate(lines, start=1):
		line = raw.rstrip('\n')
		start = 0
		while True:
			idx = line.find(ch, start)
			if idx == -1:
				break
			occ.append((i, idx + 1, line, idx))
			start = idx + 1
	return occ


def make_snippet(line: str, pos) -> str:
	before = max(0, pos - 5)
	after = min(len(line), pos + 1 + 5)
	prefix = GREY + '...' + RESET if before > 0 else ''
	suffix = GREY + '...' + RESET if after < len(line) else ''
	left = line[before:pos]
	target = line[pos]
	right = line[pos + 1 : after]
	return f'{prefix}{left}{YELLOW} {target} {RESET}{right}{suffix}'


def cmd_scan(args):
	lines = load_lines(GLYPH_FILE)
	flattened = ''.join([ln.rstrip('\n') for ln in lines])
	counts = Counter(flattened)
	duplicates = [ch for ch, c in counts.items() if c > 1]
	if not duplicates:
		print(f'{GREEN}[SCAN]{RESET} No duplication found.')
		return

	first_index = {}
	for i, ch in enumerate(flattened):
		if ch not in first_index:
			first_index[ch] = i
	duplicates.sort(key=lambda c: first_index.get(c, 0))

	for ch in duplicates:
		total = counts[ch]
		if total > 0:
			print(f"{GREEN}[SCAN]{RESET} Duplication found: '{ch}' [{total} times]")
			occs = find_all_occurrences(lines, ch)
			for ln, col, line, pos in occs:
				print(f'Line {ln} Column {col}:')
				print(make_snippet(line, pos))


def cmd_search(args):
	if not args.query:
		print('Please provide search character(s).', file=sys.stderr)
		sys.exit(2)
	joined = ''.join(args.query)
	if len(joined) > 1:
		chars = list(OrderedDict.fromkeys(joined))
	else:
		chars = [joined]
	lines = load_lines(GLYPH_FILE)
	for ch in chars:
		occs = find_all_occurrences(lines, ch)
		total = len(occs)
		if total == 0:
			print(f"{GREEN}[SEARCH]{RESET} Search result of '{ch}': None")
			continue
		else:
			print(f"{GREEN}[SEARCH]{RESET} Search result of '{ch}': [{total} {'time' if total == 1 else 'times'}]")
			for ln, col, line, pos in occs:
				print(f'Line {ln} Column {col}:')
				print(make_snippet(line, pos))


def main():
	parser = argparse.ArgumentParser(prog='check.py')
	sub = parser.add_subparsers(dest='cmd')
	p_scan = sub.add_parser('scan', help='Scan glyphs.txt for duplicated characters')
	p_scan.set_defaults(func=cmd_scan)
	p_search = sub.add_parser('search', help='Search glyphs.txt for character(s)')
	p_search.add_argument('query', nargs='+', help='Character(s) to search (arguments concatenated)')
	p_search.set_defaults(func=cmd_search)
	args = parser.parse_args()
	if not args.cmd:
		parser.print_usage()
		sys.exit(1)
	args.func(args)


if __name__ == '__main__':
	main()
