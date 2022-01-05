from colorama import init
import csv
import termcolor

from .core import OutputData, OutputDataList


# use Colorama to make Termcolor work on Windows too
init()


class Output:
    def __init__(self, data: OutputDataList, *args, **kwargs):
        self.data = data

    def put(self):
        pass


class PlainOutput(Output):
    def __init__(self, *args, **kwargs):
        self.is_colored = kwargs.get('colored', True)
        super().__init__(*args, **kwargs)

    def colored(self, val, color):
        if not self.is_colored:
            return val

        return termcolor.colored(val, color)

    def put(self):
        text = ''
        total = 0
        olist = self.data

        for o in olist:
            i = o.input_data

            text += f'Target: {self.colored(str(i), "green")}\n'
            text += f'Results found: {len(o.results)}\n'

            for n, r in enumerate(o.results):
                text += f'{n+1}) '
                total += 1

                for k in r.fields:
                    key = k.title().replace('_', ' ')
                    val = r.__dict__.get(k)
                    if val is None:
                        val = ''

                    text += f'{self.colored(key, "yellow")}: {val}\n'

                text += '\n'

            text += '-'*30 + '\n'

        text += f'Total found: {total}\n'

        return text


class CSVOutput(Output):
    def __init__(self, *args, **kwargs):
        self.filename = kwargs.get('filename', True)
        super().__init__(*args, **kwargs)

    def put(self):
        if not len(self.data) and not len(self.data[0].results):
            return ''

        fields = self.data[0].results[0].fields
        fieldnames = ['Target'] + [k.title().replace('_', ' ') for k in fields]

        with open(self.filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()

            for o in self.data:
                i = o.input_data
                row = {'Target': i}

                for r in o.results:
                    for k in fields:
                        key = k.title().replace('_', ' ')
                        val = r.__dict__.get(k)
                        row[key] = val

                    writer.writerow(row)

        return f'Results were saved to file {self.filename}'
