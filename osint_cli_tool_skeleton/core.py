import asyncio
from typing import List, Any

from aiohttp import TCPConnector, ClientSession
from bs4 import BeautifulSoup as bs

from .executor import AsyncioProgressbarQueueExecutor


class InputData:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class OutputData:
    def __init__(self, value, error):
        self.value = value
        self.error = error

    def __str__(self):
        error = ''
        if self.error:
            error = f' (error: {str(self.error)}'

        return f'{str(self.value)}{error}'


class OutputDataList:
    def __init__(self, input_data: InputData, results: List[OutputData]):
        self.input_data = input_data
        self.results = results

    def __repr__(self):
        return f'{self.input_data}: ' + ', '.join(map(str, self.results))


class Processor:
    def __init__(self):
        connector = TCPConnector(ssl=False)
        self.session = ClientSession(
            connector=connector, trust_env=True
        )

    async def close(self):
        await self.session.close()


    async def request(self, input_data: InputData) -> OutputDataList:
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

        results = OutputDataList(input_data, [OutputData(result, error)])

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

        results = await AsyncioProgressbarQueueExecutor().run(tasks)

        return results
