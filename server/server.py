import random
import time
import threading
import os
import socket
from sentence_transformers import SentenceTransformer, util
from simpleneighbors import SimpleNeighbors
import datetime
import sys
import time
#import fcntl
import signal

class SemanticSearch:
    def __init__(self, model):
        self.encoder = SentenceTransformer(model["name"])
        self.index = SimpleNeighbors(model["dims"], model["metric"])
        if model["metric"] == "angular":
            self.metric_func = util.cos_sim
        elif model["metric"] == "dot":
            self.metric_func = util.dot_score

    def load_corpus(self, filename):
        with open(f"corpus/{filename}") as f:
            self.feed(f.read().split("\n"))

    def feed(self, sentences):
        last_sentence = ''
        for i, sentence in enumerate( sentences ):
            tmp1 = sentence.split('<sep>')
            if len( tmp1 ) <= 1:
                break
            sent = tmp1[2]
            vector = self.encoder.encode(sent)
            if  i > 1:
                dist = self.metric_func(last_vector, vector)
                print( "dist:", dist )
                if dist < 0.5:
                    self.index.add_one(sentence, vector)
                    print( tmp1 )
            else:
                self.index.add_one(sentence, vector)
            
            last_sentence = sentence
            last_vector = vector
            
        self.index.build()

    def find_nearest(self, query, n=10):
        vector = self.encoder.encode(query)
        nearests = self.index.nearest(vector, n)
        res = []
        for neighbor in nearests:
            dist = self.metric_func(vector, self.index.vec(neighbor))
            res.append(neighbor + "<sep>" + str(float(dist)))
        return res

models = [
    {
        # Multi-lingual model of Universal Sentence Encoder for 15 languages:
        # Arabic, Chinese, Dutch, English, French, German, Italian, Korean, Polish, Portuguese, Russian, Spanish, Turkish.
        "name": "distiluse-base-multilingual-cased-v1",
        "dims": 512,
        "metric": "angular",
    },
    {
        # Multi-lingual model of Universal Sentence Encoder for 50 languages.
        "name": "distiluse-base-multilingual-cased-v2",
        "dims": 512,
        "metric": "angular",
    },
    {
        # Multi-lingual model of paraphrase-multilingual-MiniLM-L12-v2, extended to 50+ languages.
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "dims": 384,
        "metric": "angular",
    },
    {
        # Multi-lingual model of paraphrase-mpnet-base-v2, extended to 50+ languages.
        "name": "paraphrase-multilingual-mpnet-base-v2",
        "dims": 768,
        "metric": "angular",
    },
    {
        # This model was tuned for semantic search:
        # Given a query/question, if can find relevant passages.
        # It was trained on a large and diverse set of (question, answer) pairs.
        # 215M (question, answer) pairs from diverse sources.
        "name": "multi-qa-mpnet-base-dot-v1",
        "dims": 768,
        "metric": "dot"
    },
    {
        # This model was tuned for semantic search:
        # Given a query/question, if can find relevant passages.
        # It was trained on a large and diverse set of (question, answer) pairs.
        # 215M (question, answer) pairs from diverse sources.
        "name": "multi-qa-mpnet-base-cos-v1",
        "dims": 768,
        "metric": "angular"
    },
]

def find_model_with_name(models, name):
    for model in models:
        if model["name"] == name:
            return model
    raise NameError(f"Could not find model {name}.")

if __name__ == "__main__":

    # define model
    model = find_model_with_name(
        models, "multi-qa-mpnet-base-cos-v1")
        
    # define SemantciSearch instance。
    ss = SemanticSearch(model)
    # Load text file for search
    ss.load_corpus('00_movie_search.txt')
 
    # display "start" because long time of loading text file
    print( "start" )

    # define socket parameter
    #server_ip = "127.0.0.1"
    server_ip = "192.168.13.250"
    server_port = 10000
    listen_num = 10
    buffer_size = 1024

    # 1.create socket object
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2.Associate the IP address and port with the created socket object
    tcp_server.bind((server_ip, server_port))

    # 3.Make the created object connectable
    tcp_server.listen(listen_num)

    # open log file
    f = open( "search.log", mode = "a", encoding="UTF-8" )
    # 4.loop and keep waiting for connection
    while True:
        # 5.connect with client
        client,address = tcp_server.accept()
        print("[*] Connected!! [ Source : {}]".format(address))

        # 6.receive data
        data = client.recv(buffer_size)
        data = data.decode('UTF-8')
        print("[*] Received Data : {}\n".format(data)) # data は検索文。
        data_split = data.split( '<sep>' )
        #print( "data_split", data_split )

        # Search execution
        res = ss.find_nearest(data_split[0])
        dt_now = datetime.datetime.now()

        str_log = str( dt_now ) + "\t" + data_split[1] + "\t" + data_split[0] + "\n"
        print( "str_log", str_log )
        #fcntl.flock(f, fcntl.LOCK_EX)
        #f.write( "write test\n" )
        f.write( str_log )
        f.flush()
        
        #Loop of 10 search results
        for r in res:
            result = str( r )
            #print( result )
            # Return search results to client.
            client.send( result.encode('UTF-8') )
            time.sleep( 0.04 )
            
        # 8.terminate the connection
        str1 = "end"
        client.send( str1.encode("UTF-8") )
        print( "send end" )
        client.close()
