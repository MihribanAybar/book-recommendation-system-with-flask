import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

books = pd.read_csv('dataset/books.csv')
book_tags = pd.read_csv('dataset/book_tags.csv')
tags = pd.read_csv('dataset/tags.csv')

# Kitap etiketlerini birleştirme
book_tags = book_tags.merge(tags, left_on='tag_id', right_on='tag_id', how='inner')

# Etiketleri birleştirme
book_tags_agg = book_tags.groupby('goodreads_book_id')['tag_name'].apply(lambda x: ' '.join(x)).reset_index()
books = books.merge(book_tags_agg, left_on='book_id', right_on='goodreads_book_id', how='left')

# Eksik etiketleri boş string ile doldurma
books['tag_name'] = books['tag_name'].fillna('')

# Özellikleri birleştirme
books['combined_features'] = books['tag_name'] + ' ' + books['authors']

# Vektörleştirme
count_vectorizer = CountVectorizer(stop_words='english')
count_matrix = count_vectorizer.fit_transform(books['combined_features'])

# Kosinüs benzerliği matrisi oluşturma
cosine_sim = cosine_similarity(count_matrix, count_matrix)

def get_book_recommendations(title, data, cosine_sim):
    try:
        # Kitabın indeksini bulma
        idx = data[data['title'] == title].index[0]
        
        # Kitaplar arasındaki benzerlik puanlarını alma
        sim_scores = list(enumerate(cosine_sim[idx]))
        
        # Benzer kitapları puanlarına göre sıralama
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # En benzer 5 kitabın indekslerini alma
        sim_scores = sim_scores[1:6]
        book_indices = [i[0] for i in sim_scores]
        
        # Benzer kitapların bilgilerini döndürme
        return data.iloc[book_indices][['title', 
                                        'authors', 
                                        'image_url', 
                                        'average_rating', 
                                        'ratings_count']].to_dict('records')
    except IndexError:
        return [{"title": "Kitap bulunamadı", 
                 "authors": "", 
                 "image_url": "", 
                 "average_rating": 0, 
                 "ratings_count": 0}]