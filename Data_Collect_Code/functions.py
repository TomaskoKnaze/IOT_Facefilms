import re
import pysrt



def subtitle_parse(subtitle, film_runtime):

    subs = pysrt.open(subtitle)
    sub_length = (len(subs))
    film_length = film_runtime
    final_final_text = []



    for u in range(film_length+1):
        final_final_text.append(0)



    indexes = []
    text = []
    starting_h = []
    starting_m = []
    starting_s = []

    ending_h = []
    ending_m = []
    ending_s = []

    for x in range(sub_length):
        subtitle = subs[x]

        index = x
        sub_text = subtitle.text
        
        start_hour = subtitle.start.hours
        start_minute = subtitle.start.minutes
        start_second = subtitle.start.seconds

        end_hour = subtitle.end.hours
        end_minute = subtitle.end.minutes
        end_second = subtitle.end.seconds


        indexes.append(index)
        text.append(sub_text)

        starting_h.append(start_hour)
        starting_m.append(start_minute)
        starting_s.append(start_second)

        ending_h.append(end_hour)
        ending_m.append(end_minute)
        ending_s.append(end_second)

    total_second_start = []
    total_second_end = []

    for y in range(sub_length):
        s_seconds = 0
        s_seconds = starting_h[y]*3600 + starting_m[y]*60 + starting_s[y]
        total_second_start.append(s_seconds)

        e_seconds = 0
        e_seconds = ending_h[y]*3600 + ending_m[y]*60 + ending_s[y]
        total_second_end.append(e_seconds)
        
    text_stripped = []
    for k in text:
        text_stripped.append(k.strip('\n'))

    counter = 0

    for n in range(len(total_second_start)):
        amount = total_second_end[n] - total_second_start[n] + 1
        for i in range(amount):
            position = total_second_start[n] -1 + i
            final_final_text[position] = text_stripped[counter]
        counter += 1

    return final_final_text


def most_frequent(List): 
    counter = 0
    num = List[0] 
      
    for i in List: 
        curr_frequency = List.count(i) 
        if(curr_frequency> counter): 
            counter = curr_frequency 
            num = i 
  
    return num 



    