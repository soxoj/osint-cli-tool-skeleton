import aiohttp
import asyncio
import json

from aiohttp import web
from aiohttp.web import HTTPNotFound

from .core import Processor, InputData, OutputDataListEncoder


class CheckServer:
    """
        Simple HTTP server
    """
    def __init__(self, addr, *args, **kwargs):
        self.addr = addr
        self.proxy = kwargs.get('proxy')
        self.loop = kwargs.get('loop')

    async def status(self, request):
        """
            Default page answer
        """
        return web.Response()

    async def check(self, request):
        """
            Check targets list
        """
        result = {}

        try:
            request_data = await request.json()

            targets = request_data.get('targets', [])

            input_data = []
            # convert input to output
            processor = Processor(
                no_progressbar=True,
                proxy=self.proxy,
            )

            for t in targets:
                input_data.append(InputData(t))

            if not input_data:
                await processor.close()
                return web.json_response(result)

            output_data = await processor.process(input_data)
            clean_data = [d for d in output_data if d]
            json_data = json.dumps(clean_data, cls=OutputDataListEncoder)
            result = json.loads(json_data)

            await processor.close()

        except Exception as e:
            print(e)

        return web.json_response(result)

    async def start(self, debug=False):
        """
            Starts an HTTP server
        """
        app = web.Application(loop=asyncio.get_event_loop())

        routes = [
            web.get('/', self.status),
            web.post('/check', self.check),
        ]

        app.add_routes(routes)

        host, port = self.addr.split(':')

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, host, port)
        await site.start()

        print('Server started')
        await asyncio.Event().wait()
