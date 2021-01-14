import pymongo
import numpy as np
from pymongo import MongoClient
import pandas as pd
import imdb


emotion_labels = ["Angry", "Happy", "Neutral", "Sad", "Surprised", "None"]

def get_dataframe(collection_list,db):
    film_names = []
    df = pd.DataFrame()
    for collection in collection_list:
        col = db[collection] 
        for doc in col.find():
            current_doc = doc
            length = len(doc['emotions'])
            id_number = doc['_id']
            name_film = doc['name']
            
            emotion_index_list = doc['emotions']
            id_list = []
            film_name_list = []
            
            emotion_name_list = []
            

            for m in range(length):
                id_list.append(id_number)
                film_name_list.append(name_film)

            for emotion in emotion_index_list:
                emotion_name_list.append(emotion_labels[emotion])
            
            current_doc['emotions'] = emotion_name_list
            current_doc['_id'] = id_list
            current_doc['name'] = film_name_list
            
            df_temp = pd.DataFrame.from_dict(current_doc)
            #print(df_temp)
            df = df.append(df_temp)
            df.reset_index(drop=True, inplace=True)
        film_names.append(name_film)

    results = df
    return results 

def if_movement_section(index, rel_movement_list, no_movement, some_movement, lot_movement):
    rating_list = []
    if rel_movement_list[index] < 2.3:
        rating_list.append(no_movement)
    elif rel_movement_list[index] >= 2.3 and rel_movement_list[index] <= 4.3:
        rating_list.append(some_movement)
    elif rel_movement_list[index] > 4.3:
        rating_list.append(lot_movement)
    return rating_list

def all_same(items):
    return all(x == items[0] for x in items)


def get_dataframe2(collection_list,db):
    
    df_list = []
    for collection in collection_list:
        df = pd.DataFrame()
        col = db[collection] 
        for doc in col.find():
            current_doc = doc
            length = len(doc['emotions'])
            id_number = doc['_id']
            name_film = doc['name']
            
            emotion_index_list = doc['emotions']
            id_list = []
            film_name_list = []
            
            emotion_name_list = []
            

            for m in range(length):
                id_list.append(id_number)
                film_name_list.append(name_film)

            for emotion in emotion_index_list:
                emotion_name_list.append(emotion_labels[emotion])
            
            current_doc['emotions'] = emotion_name_list
            current_doc['_id'] = id_list
            current_doc['name'] = film_name_list
            
            df_temp = pd.DataFrame.from_dict(current_doc)
            #print(df_temp)
            df = df.append(df_temp)
            df.reset_index(drop=True, inplace=True)
        df_list.append(df)


    #results = df
    return df_list 

def cummulative_rating_calculator(dataframe_list,film_name_list):
    results = []
    updated_dataframe_list = []
    for h in range(len(film_name_list)):
        film = film_name_list[h]
        result = []
        dataframe = dataframe_list[h]
        rating_seconds = dataframe['rating_seconds'].tolist()
        cummulative_score = 50
        cummulative_rating = []
        for k in rating_seconds:
            cummulative_score += k
            cummulative_rating.append(cummulative_score)
        dataframe['cummulative_rating'] = cummulative_rating
        results.append([film, dataframe])
    return results

def rating_calculator(dataframe_list,film_name_list):
    results = []
    updated_dataframe_list = []
    for h in range(len(film_name_list)):
        film = film_name_list[h]
        result = []
        dataframe = dataframe_list[h]
        

        rating_seconds = []
        base_rating = 50

        relevant_emotions = dataframe['emotions'].tolist()
        relevant_timestamp = dataframe['timestamp'].tolist()
        relevant_movement = dataframe['movement'].tolist()


        multiplier = 5400/len(relevant_emotions)
        movement_delta = []

        for j in range (len(relevant_emotions)):
            buffer = []
            buffer.append(relevant_emotions[j])
            if relevant_emotions[j] == 'Angry':
                rating_seconds.extend(if_movement_section(j, relevant_movement, 0.00370, 0.00185, -0.00556 ))
            elif relevant_emotions[j] == 'Happy':
                rating_seconds.extend(if_movement_section(j, relevant_movement, 0.01963, 0.01556, 0.00750 ))
            elif relevant_emotions[j] == 'Neutral':
                rating_seconds.extend(if_movement_section(j, relevant_movement, 0.00128, 0.00093, -0.00570 ))
            elif relevant_emotions[j] == 'Sad':
                rating_seconds.extend(if_movement_section(j, relevant_movement, 0.00750, 0.01163, 0.00185 ))
            elif relevant_emotions[j] == 'Surprised':
                rating_seconds.extend(if_movement_section(j, relevant_movement, 0.02186, 0.02370, 0.00750 ))
            elif relevant_emotions[j] == 'None':
                rating_seconds.extend(if_movement_section(j, relevant_movement, -0.00093, -0.00185, 0.00278 ))

            if len(buffer) == 4:
                if all_same(buffer) == True:
                    if buffer[2] == 'Angry':
                        rating_seconds[j] = 0.008
                        rating_seconds[j-1] = 0.008
                        rating_seconds[j-2] = 0.008
                        rating_seconds[j-3] = 0.008
                        rating_seconds[j-4] = 0.008
                    elif buffer[2] == 'Sad':
                        rating_seconds[j] = 0.09
                        rating_seconds[j-1] = 0.09
                        rating_seconds[j-2] = 0.09
                        rating_seconds[j-3] = 0.09
                        rating_seconds[j-4] = 0.09
                    elif buffer[2] == 'Surprised':
                        rating_seconds[j] = 0.01
                        rating_seconds[j-1] = 0.01
                        rating_seconds[j-2] = 0.01
                        rating_seconds[j-3] = 0.01
                        rating_seconds[j-4] = 0.01
                    elif buffer[2] == 'Happy':
                        rating_seconds[j] = 0.007
                        rating_seconds[j-1] = 0.007
                        rating_seconds[j-2] = 0.007
                        rating_seconds[j-3] = 0.007
                        rating_seconds[j-4] = 0.007
                    elif buffer[2] == 'None':
                        rating_seconds[j] = -0.005
                        rating_seconds[j-1] = -0.005
                        rating_seconds[j-2] = -0.005
                        rating_seconds[j-3] = -0.005
                        rating_seconds[j-4] = -0.005
                    else:
                        None
                else:
                    buffer.pop(0)

            rating_seconds[j] = rating_seconds[j]*multiplier
            if j == 0:
                movement_delta.append(0)
            else:
                movement_delta.append(relevant_movement[j] - relevant_movement[j-1])

            if abs(movement_delta[j]) > 3 and relevant_emotions[j] == 'Angry':
                rating_seconds[j] = 0.012
            elif abs(movement_delta[j]) > 4 and relevant_emotions[j] == 'Happy':
                rating_seconds[j] = 0.011
            elif abs(movement_delta[j]) > 4.5 and relevant_emotions[j] == 'Surprised':
                rating_seconds[j] = 0.013
            else:
                None

            base_rating += rating_seconds[j]

        dataframe['rating_seconds'] = rating_seconds
        dataframe['movement_delta'] = movement_delta
        #updated_dataframe_list.append(dataframe)
        
        results.append([film,base_rating, dataframe])
    
    return results


def get_favourite_section(dataframe_list, film_name_list):
    results = []
    for h in range(len(film_name_list)):
        film = film_name_list[h]
        favourite_section_start = 0
        previous_rolling_sum = 0
        dataframe = dataframe_list[h]
        rating_list = dataframe['rating_seconds'].tolist()
        lines = dataframe['text'].tolist()
        rolling_list = []
        text_list = []
        for o in range(len(rating_list)):
            rating_second = rating_list[o]
            
            
            rolling_list.append(rating_second)

            if len(rolling_list) == 20:
                rolling_list.pop(0)
                rolling_sum = sum(rolling_list)
                
                if rolling_sum > previous_rolling_sum:
                    previous_rolling_sum = rolling_sum
                    favourite_section_start = o-19
                else:
                    None
        
                
        

        for p in range(19):
            text_list.append(lines[favourite_section_start+p])

        result = [film, favourite_section_start, text_list]
        results.append(result)

    return results


def get_predominant_emotion(dataframe_list, film_name_list):
    results = []
    for g in range(len(film_name_list)):
        film = film_name_list[g]
        dataframe = dataframe_list[g]

        all_emotions = []
        happy = ['happy']
        sad = ['sad']
        surprised = ['surprised']
        angry = ['angry']

        emotions_list = dataframe['emotions'].tolist()
        for emotion in emotions_list:
            if emotion == 'Happy':
                happy.append(1)
            elif emotion == 'Sad':
                sad.append(1)
            elif emotion == 'Surprised':
                surprised.append(1)
            elif emotion == 'Angry':
                angry.append(1)
            else:
                None
        all_emotions.append(happy)
        all_emotions.append(sad)
        all_emotions.append(surprised)
        all_emotions.append(angry)

        sorted_emotions = sorted(all_emotions, key = len, reverse = True)
        first = sorted_emotions[0][0]
        second = sorted_emotions[1][0]
        third = sorted_emotions[2][0]

        #frequency_list = dataframe.emotions.value_counts()
        result = [film,[first, second, third]]
        results.append(result)

    return results

def get_leaderboards_dataframe(rating_list):
    film_unordered = []
    ratings = []
    df = pd.DataFrame()
    for couple in rating_list:
        film_unordered.append(couple[0])
        ratings.append(couple[1])
    df['name'] = film_unordered
    df['rating'] = ratings
    sorted_df = df.sort_values(by=['rating'], ascending=False)
    return sorted_df

    
def get_imdb_score(film_name):
    try:
        ia = imdb.IMDb()
        name = film_name.replace('_' , ' ')

        movies = ia.search_movie(name)

        movie_id = movies[0].movieID


        film_object = ia.get_movie(movie_id)
        rating = film_object.data['rating']
        #synopsis = film_object.data['synopsis']
        cast = film_object.data['cast']
        director = film_object.data['director']
        director1 = director[0]
        director2 = director1['name']
        actors = cast[:5]
        parsed_actors = ""
        for actor in actors:
            actor_name = actor['name']
            parsed_actors += str(actor_name)
            parsed_actors += str(', ')

        link = ia.get_imdbURL(film_object)

        result = [film_name, rating, director2, parsed_actors, link ]
    except KeyError:
        result = [film_name, 'No rating Found', 'No director info found', 'Information on actors was not found', 'No link :(' ]
    return result
    

def get_average_movement(dataframe_list, film_name_list):
    results = []
    for h in range(len(film_name_list)):
        film_name = film_name_list[h]
        dataframe = dataframe_list[h]
        movement_list = dataframe['movement'].tolist()
        average_movement = sum(movement_list)/len(movement_list)

        result = [film_name,average_movement]
        results.append(result)
    return results

def get_distraction_time(dataframe_list, film_name_list):
    results = []
    for h in range(len(film_name_list)):
        film_name = film_name_list[h]
        dataframe = dataframe_list[h]
        emotions_list = dataframe['emotions'].tolist()
        no_attention_list = []

        for emotion in emotions_list:
            if emotion == 'None':
                no_attention_list.append(1)
            else:
                None
        distracted_time = len(no_attention_list)

        result = [film_name, distracted_time]
        results.append(result)
    return results


def get_total_watchtime(dataframe_list, film_name_list):
    total_time = 0
    for index in range(len(film_name_list)):
        dataframe = dataframe_list[index]
        sec_list = dataframe['timestamp'].tolist()
        total_time += len(sec_list)

    return total_time

def get_average_rating(rating_list):
    sum_all = 0
    for couple in rating_list:
        sum_all += couple[1]

    average = sum_all/len(rating_list)
    return average