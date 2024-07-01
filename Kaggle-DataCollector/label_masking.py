from nltk.corpus import wordnet
from nltk.stem import LancasterStemmer
import os
import random
import nltk

stemmer = LancasterStemmer()


def add_spaces_around_slash(text):
    modified_text = ""
    for char in text:
        if char == '/':
            modified_text += ' / '
        else:
            modified_text += char
    return modified_text

def remove_extra_spaces(text):
    punctuation_marks = ['.', ',', '!', '?', ';', ':',"'"]
    for mark in punctuation_marks:
        text = text.replace(' ' + mark, mark)
    return ' '.join(text.split())

def get_synonyms(word, pos):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.name() != word and lemma.synset().pos() == pos:
                synonyms.append(lemma.name())
    if (len(synonyms)==0):
        return word
    else:
        return set(synonyms)

def get_pos(word):
    # Get the part of speech using WordNet
    synsets = wordnet.synsets(word)
    if synsets:
        return synsets[0].pos()
    return None

def replace_with_synonym(word, pos):
    
    # synonyms = get_synonyms("interdependence", pos)
    synonyms = get_synonyms(word, pos)

    
    if synonyms!=word:
        synonym = random.choice(list(synonyms))
        
        if word.endswith('s'):
            return synonym + 's'
        
        elif word.endswith('ing'):
            if synonym.endswith('e'):
                return synonym[:-1] + 'ing'
            else:
                return synonym + 'ing'
        
        elif word.endswith('ed'):
            if synonym.endswith('e'):
                return synonym[:-1] + 'ed'
            else:
                return synonym + 'ed'
        
        return synonym  # If none of the above conditions are met, return the synonym without any suffix
    
    return word

def get_stem(word):
    return stemmer.stem(word)

def process_text(text, term):
    text = add_spaces_around_slash(text=text)
    stem = get_stem(term)
    words = nltk.word_tokenize(text)
    flag = False
    modified_words = []
    if term in ['regression', 'classification', 'forecasting']:
        for word in words:
            replacement = word
            if word.lower() in ['regression', 'classification', 'forecasting', 'classifying']:
                replacement = 'prediction'
            elif word.lower() == 'classify' or word.lower() == 'forecast' :
                replacement = 'predict'

            elif word.lower() == 'forecasted' or word.lower() == 'classified':
                replacement = 'predicted'
            
            elif word.lower() == 'forecasts' or word.lower() == 'classifies':
                replacement = 'predicts'

            elif word.lower() == 'regressor' or word.lower() == 'classifier':
                replacement = 'model'
            
            elif word.lower() == 'regressors' or word.lower() == 'classifiers':
                replacement = 'models'
            elif word.lower() == 'classifications' or word.lower() == 'regressions':
                replacement = 'predictions'
  
    else:
        for word in words:
            replacement = word
            if get_stem(word.lower()) == stem:
                pos = get_pos(word)
                replacement = replace_with_synonym(word, pos)
                
                while get_stem(replacement.lower()) == stem or replacement.lower() == term.lower():
                    replacement = replace_with_synonym(word, pos)
                    
                modified_words.append(replacement)
            else:
                modified_words.append(word)

        modified_words.append(replacement)

    
    modified_text = ' '.join(modified_words)
    modified_text = remove_extra_spaces(modified_text)
    
    return modified_text

def process_file(file_path, term):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    modified_content = process_text(content, term)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)

def process_folder(folder_path, term):
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    for file in files:
        file_path = os.path.join(folder_path, file)
        process_file(file_path, term)

# Example usage:
folder_path = 'correlation'  # Replace with your folder path
term_to_replace = "correlation"  # Change to your desired term
process_folder(folder_path, term_to_replace)
