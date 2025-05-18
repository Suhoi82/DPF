import pandas as pd 
from collections import defaultdict
import numpy as np 
from math import log
import os

def remove_paragraph_indents(text):
    cleaned_lines = [line.lstrip() for line in text.splitlines()]
    return '\n'.join(cleaned_lines)

folder_path =
texts = []

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            content = file.read()
            cleaned_content = remove_paragraph_indents(content)
            texts.append(cleaned_content)

corpus = ' '.join(texts)
stop_words = set(['آنجا','آنکه','های','ست','کرده','ازین','ازان','باز','گردد','،','گشت','فی','زین','کو','هست','چنین','برای','شود','کس','کز','بهر','همچو','سوی','پی','همی','شمارهٔ','یا','چو','مر','گفت','برات','چون', 'هیچ', 'صد','دارد','داری', 'نیست', 'است','گوید','چی', 'چه', 'اگر', 'هر', 'را', 'از', 'ز', 'چهار', 'سه', 'یک', 'شما', 'وی', 'انها', 'ما', 'او', 'تو', 'من', 'دو', 'پیش', 'گر', 'می', 'و', 'در', 'کی', 'شد', 'کرد', 'گرچه', 'گاه', 'گه', 'زان', 'که', 'به', 'بر', 'آن', 'تا', 'این', 'اندر', 'آندر', 'اینجا', 'درین', 'بود', 'بی', 'آمد', 'چون', 'با', 'ای', 'هم', 'باشد', 'ترا', '-', ':', 'سر'])

def filter_stop_words(text):
    words = text.split()
    return [word for word in words if word not in stop_words]

filtered_words = filter_stop_words(corpus)

class CooccurrenceAnalyzer:
    def __init__(self, words_list=None, target_pairs=None, window_size=40, freq_window=5):
        self.window_size = window_size
        self.freq_window = freq_window
        self.total_pairs = 0
        self.dpf_matrix = None
        self.target_pairs = target_pairs
        
        if words_list:
            self.fit(words_list)
    
    def fit(self, words_list):
        self._build_cooccurrence_matrix(words_list)
        self._calculate_association_measures()
        return self
    
    def _build_cooccurrence_matrix(self, words_list):
        word_freq = defaultdict(int)
        cooccur = defaultdict(int)
        
        n = len(words_list)
        
        for word in words_list:
            word_freq[word] += 1
                
        for i in range(n):
            for j in range(i+1, min(i+self.window_size+1, n)):
                w1, w2 = words_list[i], words_list[j]
                if self.target_pairs is None or (w1, w2) in self.target_pairs or (w2, w1) in self.target_pairs:
                    cooccur[(w1, w2)] += 1
        
        self.cooccur_df = pd.DataFrame(
            [(w1, w2, cnt) for (w1, w2), cnt in cooccur.items()],
            columns=['focal', 'bound', 'count']
        )
        
        self.total_words = sum(word_freq.values())
        self.total_pairs = self.cooccur_df['count'].sum() if not self.cooccur_df.empty else 0
    
    def _calculate_association_measures(self):
        if self.cooccur_df.empty:
            self.dpf_matrix = pd.DataFrame(columns=['focal', 'bound', 'dpf'])
            return
            
        df = self.cooccur_df.copy()
        
        focal_freq = df.groupby('focal')['count'].sum().rename('focal_e')
        bound_freq = df.groupby('bound')['count'].sum().rename('bound_e')
        
        df = df.join(focal_freq, on='focal').join(bound_freq, on='bound')
        
        df['focal_e'] = (df['focal_e'] // self.freq_window) + 1
        df['bound_e'] = (df['bound_e'] // self.freq_window) + 1
        
        df['o11'] = df['count']
        df['o12'] = df['focal_e'] - df['count']
        df['o21'] = df['bound_e'] - df['count']
        df['o22'] = self.total_pairs - (df['focal_e'] + df['bound_e'] - df['count'])
        
        df['e11'] = (df['focal_e'] * df['bound_e']) / self.total_pairs
        
        df['dpf'] = np.log(df['o11'] + 1) / np.log(df['e11'] + 1)
        
        self.dpf_matrix = df
    
    def get_dpf_for_pairs(self, pairs=None):
        if self.dpf_matrix is None:
            raise ValueError("Сначала необходимо обработать корпус методом fit()")
            
        if pairs is None:
            return self.dpf_matrix[['focal', 'bound', 'dpf']]
        
        result = []
        for pair in pairs:
            mask = ((self.dpf_matrix['focal'] == pair[0]) &
                   (self.dpf_matrix['bound'] == pair[1]))
            if mask.any():
                result.append(self.dpf_matrix.loc[mask, ['focal', 'bound', 'dpf']].iloc[0])
            else:
                result.append({'focal': pair[0], 'bound': pair[1], 'dpf': 0.0})
        
        return pd.DataFrame(result)


target_pairs = [

analyzer = CooccurrenceAnalyzer(words_list=filtered_words, target_pairs=target_pairs)

results = analyzer.get_dpf_for_pairs()
print("DPF для заданных пар слов (с учетом направления):")
print(results)