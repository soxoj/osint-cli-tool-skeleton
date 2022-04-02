import asyncio
import logging
from json import JSONEncoder
from typing import List, Any

from aiohttp import TCPConnector, ClientSession

from .executor import AsyncioProgressbarQueueExecutor, AsyncioSimpleExecutor


class InputData:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class OutputData:
    def __init__(self, value, code, error):
        self.value = value
        self.code = code
        self.error = error

    @property
    def fields(self):
        fields = list(self.__dict__.keys())
        fields.remove('error')

        return fields

    def __str__(self):
        error = ''
        if self.error:
            error = f' (error: {str(self.error)}'

        result = ''

        for field in self.fields:
            field_pretty_name = field.title().replace('_', ' ')
            value = self.__dict__.get(field)
            if value:
                result += f'{field_pretty_name}: {str(value)}\n'

        result += f'{error}'
        return result


class OutputDataList:
    def __init__(self, input_data: InputData, results: List[OutputData]):
        self.input_data = input_data
        self.results = results

    def __repr__(self):
        return f'Target {self.input_data}:\n' + '--------\n'.join(map(str, self.results))


class OutputDataListEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, OutputDataList):
            return {'input': o.input_data, 'output': o.results}
        elif isinstance(o, OutputData):
            return {k:o.__dict__[k] for k in o.fields}
        else:
            return o.__dict__


class Processor:
    def __init__(self, *args, **kwargs):
        from aiohttp_socks import ProxyConnector

        # make http client session
        proxy = kwargs.get('proxy')
        self.proxy = proxy
        if proxy:
            connector = ProxyConnector.from_url(proxy, ssl=False)
        else:
            connector = TCPConnector(ssl=False)

        self.session = ClientSession(
            connector=connector, trust_env=True
        )
        if kwargs.get('no_progressbar'):
            self.executor = AsyncioSimpleExecutor()
        else:
            self.executor = AsyncioProgressbarQueueExecutor()

        self.logger = logging.getLogger('processor')

    async def close(self):
        await self.session.close()


    async def request(self, input_data: InputData) -> OutputDataList:
        from bs4 import BeautifulSoup as bs
        status = 0
        result = None
        error = None

        try:
            url = input_data.value
            if not url.startswith('http'):
                url = 'https://' + url

            response = await self.session.get(url)

            status = response.status
            response_content = await response.content.read()
            charset = response.charset or "utf-8"
            html = response_content.decode(charset, "ignore")

            soup = bs(html, 'html.parser')
            title = soup.find('title').string
            result = title

        except Exception as e:
            error = e
            self.logger.error(e, exc_info=False)

        results = OutputDataList(input_data, [OutputData(result, status, error)])

        return results


    async def process(self, input_data: List[InputData]) -> List[OutputDataList]:
        tasks = [
            (
                self.request, # func
                [i],          # args
                {}            # kwargs
            )
            for i in input_data
        ]

        results = await self.executor.run(tasks)

        return results
