# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
from utils import loggerinfo, loggererror


class EsBackends(object):
    def __init__(self, index_name, doc_name):
        self.es = Elasticsearch(hosts=["192.168.188.157:9200"])
        self.index_name = index_name
        self.doc_name = doc_name
        if self.es.indices.exists(index=self.index_name) is not True:
            self.create_index()

    def create_index(self):
        _index_mappings = {
            "mappings": {
                self.doc_name: {
                    "properties": {
                        "title": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word",
                        },
                        "link": {"type": "text", "index": True, "analyzer": "standard"},
                        "date": {"type": "text", "index": True},
                        "site_name": {"type": "text", "index": True},
                    }
                }
            }
        }
        _index_books = {
            "mappings": {
                self.doc_name: {
                    "properties": {
                        "title": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word",
                        },
                        "author": {
                            "type": "text",
                            "index": True,
                            "analyzer": "ik_max_word",
                        },
                    }
                }
            }
        }
        if self.index_name == "crawled_books":
            res = self.es.indices.create(index="crawled_books", body=_index_books)
            if res["acknowledged"] is not True:
                loggerinfo.info("the index have existed")
        else:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            if res["acknowledged"] is not True:
                loggerinfo.info("the index have existed")

    def index_data(self, data):
        try:
            self.es.index(index=self.index_name, doc_type=self.doc_name, body=data)
            # loggerinfo.info("Insert successfully")
        except Exception as e:
            loggererror.error("Insert error:{}".format(e))
            pass

    def search_data(self, body):
        res = self.es.search(index=self.index_name, doc_type=self.doc_name, body=body)
        return res
