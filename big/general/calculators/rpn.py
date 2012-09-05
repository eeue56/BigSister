from operator import add, floordiv as div, mul, sub

class UnbalancedOperators(Exception):
	pass


class ReversePolishExpression(object):

	def __init__(self, parser=None):
		self.operators = []
		self.numbers = []

		if parser is None:
			self.parser = self._convert_to_number

		self.actions = {'+' : add,
						'/' : div,
						'*' : mul,
						'-' : sub,
						'^' : pow}

	def _is_int(self, num):
		return int(num + 0) == num

	def _convert_to_number(self, string):
		if '.' in string:
			return float(string)
		return int(string)

	def _break_into_parts(self, parts):
		parts = (part.strip() for part in parts.split())

		for part in parts:
			if part in self.actions:
				self.operators.append(part)
			else:
				try:
					self.numbers.append(self.parser(part))
				except:
					pass

	def _next_operator(self):
		while True:
			if len(self.operators) == 0:
				raise StopIteration
			yield self.operators.pop(0)

	def calulate(self, whole):
		self._break_into_parts(whole)

		for operator in self._next_operator():
			
			if len(self.numbers) < 2:
				raise UnbalancedOperators('There are too many operators!')

			first = self.numbers.pop(0)
			second = self.numbers.pop(0)
			
			result = self.actions[operator](first, second)

			self.numbers.insert(0, result)
		return self.numbers[0]


if __name__ == '__main__':
	rpn = ReversePolishExpression()
	print rpn.calulate('10.5456546 4.1 *')
	print rpn.calulate('5 +')
		