from requests import get as get_request	
	
def levenshtein(current_word, next_word):
	''' Says how similar a word is to the next word '''

	if current_word == '':
		return len(next_word)
	
	if len(current_word) < len(next_word):
		current_word, next_word = next_word, current_word
		
	previous_row = xrange(len(next_word) + 1)
	
	for i, current_character in enumerate(current_word):
		current_row = [i + 1]
		
		for j, next_character in enumerate(next_word):
			insertions = previous_row[j + 1] + 1
			deletions = current_row[j] + 1 
			substitutions = previous_row[j] + (current_character != next_character)
			current_row.append(min(insertions, deletions, substitutions))
			
		previous_row = current_row[:]
	return previous_row[-1]

def crop_string(start_string, crop_string, after=True):
	if after:
		return start_string[start_string.find(crop_string) + len(crop_string):]
	return start_string[:start_string.find(crop_string)]
