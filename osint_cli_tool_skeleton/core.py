from typing import List, Any


class InputData:
	def __init__(self, value: str):
		self.value = value

	def __str__(self):
		return self.value

	def __repr__(self):
		return self.value


class OutputData:
	def __init__(self, input_data: InputData, results: List[Any]):
		self.input_data = input_data
		self.results = results

	def __repr__(self):
		return f'{self.input_data}: ' + ', '.join(self.results)


def process(input_data: List[InputData]) -> List[OutputData]:
	results = []
	for i in input_data:
		results.append(OutputData(i, []))

	return results
