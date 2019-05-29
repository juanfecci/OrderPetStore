# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app
from google.cloud import datastore

import datetime
import json


builtin_list = list


def init_app(app):
    pass


def get_client():
    return datastore.Client(current_app.config['PROJECT_ID'])


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()

    entity['id'] = entity.key.id
    return entity
# [END from_datastore]


def returnJson(entity):
    result = dict()
    result["id"] = entity["id"]
    result["userId"] = entity["userId"]
    try:
        result["userName"] = entity["userName"]
    except:
        pass
    result["orderDate"] = repr(entity["orderDate"])
    result["total"] = entity["total"]
    result["status"] = entity["status"]

    ds = get_client()

    query = ds.query(kind='Item')
    query.add_filter('orderId', '=', entity['id'])
    query_iterator = list(query.fetch())

    result["items"] = []
    for item in query_iterator:
        aux = {}
        aux["id"] = item["itemId"]
        try:
            aux["name"] = item["name"]
        except:
            pass
        aux["price"] = item["price"]
        aux["quantity"] = item["quantity"]
        aux["description"] = item["description"]
        result["items"].append(aux)

    result["paymentDate"] = repr(entity["paymentDate"])
    result["paymentTotal"] = entity["paymentTotal"]
    result["paymentDetail"] = entity["paymentDetail"]
    result["addressCountry"] = entity["addressCountry"]
    result["addressRegion"] = entity["addressRegion"]
    result["addressCity"] = entity["addressCity"]
    result["addressCommune"] = entity["addressCommune"]
    result["addressStreet"] = entity["addressStreet"]
    result["addressNumber"] = entity["addressNumber"]

    return json.dumps(result)

def update(data, id=None):
    ds = get_client()
    if id:
        key = ds.key('Order', int(id))
    else:
        key = ds.key('Order')

    entity = datastore.Entity(
        key=key,
        exclude_from_indexes=['status'])

    entity.update({
        "userId":data["userId"],
        "userName":data["userName"],
        "orderDate":datetime.datetime.utcnow(),
        "total": 0,
        "status":data["status"],
        "paymentDate":datetime.datetime.utcnow(),
        "paymentTotal":0,
        "paymentDetail":"WAITING",
        "addressCountry":data["addressCountry"],
        "addressRegion":data["addressRegion"],
        "addressCity":data["addressCity"],
        "addressCommune":data["addressCommune"],
        "addressStreet":data["addressStreet"],
        "addressNumber":data["addressNumber"]
    })

    ds.put(entity)

    total = 0
    for item in data["items"]:
        key = ds.key('Item')

        entity2 = datastore.Entity(
            key=key,
            exclude_from_indexes=['description'])

        entity2.update({
            "orderId": entity.key.id,
            "itemId":item["id"],
            "name":item["name"],
            "price":item["price"],
            "quantity":item["quantity"],
            "description":item["description"],
        })

        total += int(item["price"]) * int(item["quantity"])
        ds.put(entity2)

    entity.update({
        "total":total,
        "paymentTotal":total
    })
    ds.put(entity)

    entity.update({
        "id": entity.key.id,
    })
    ds.put(entity)

    return returnJson(entity)

create = update

def get(id):
    ds = get_client()
    key = ds.key('Order', int(id))
    entity = ds.get(key)
    return returnJson(entity)

def listAll():
    ds = get_client()
    query = ds.query(kind='Order')
    query_iterator = list(query.fetch())

    result = []
    for item in query_iterator:
        result.append(json.loads(returnJson(item)))

    return json.dumps(result)

def listByUser(userId):
    ds = get_client()
    query = ds.query(kind='Order')
    query.add_filter('userId', '=', int(userId))
    query_iterator = list(query.fetch())

    result = []
    for item in query_iterator:
        result.append(json.loads(returnJson(item)))

    return json.dumps(result)

def listItems(orderId):
    ds = get_client()
    query = ds.query(kind='Item')
    query.add_filter('orderId', '=', int(orderId))
    query_iterator = list(query.fetch())

    result = []
    for item in query_iterator:
        aux = {}
        aux["id"] = item["itemId"]
        try:
            aux["name"] = item["name"]
        except:
            pass
        aux["price"] = item["price"]
        aux["quantity"] = item["quantity"]
        aux["description"] = item["description"]
        result.append(aux)

    return json.dumps(result)

def paymentGet(orderId):
    ds = get_client()
    key = ds.key('Order', int(orderId))
    entity = ds.get(key)

    result = dict()
    result["paymentDate"] = repr(entity["paymentDate"])
    result["paymentTotal"] = entity["paymentTotal"]
    result["paymentDetail"] = entity["paymentDetail"]

    return json.dumps(result)

def paymentUpdate(orderId, data):
    ds = get_client()
    key = ds.key('Order', int(orderId))
    entity = ds.get(key)

    entity['paymentDetail'] = data["detail"]
    ds.put(entity)

    result = dict()
    result["paymentDate"] = repr(entity["paymentDate"])
    result["paymentTotal"] = entity["paymentTotal"]
    result["paymentDetail"] = entity["paymentDetail"]

    return json.dumps(result)

def addressGet(orderId):
    ds = get_client()
    key = ds.key('Order', int(orderId))
    entity = ds.get(key)

    result = dict()
    result["addressCountry"] = entity["addressCountry"]
    result["addressRegion"] = entity["addressRegion"]
    result["addressCity"] = entity["addressCity"]
    result["addressCommune"] = entity["addressCommune"]
    result["addressStreet"] = entity["addressStreet"]
    result["addressNumber"] = entity["addressNumber"]

    return json.dumps(result)

def delete(id):
    ds = get_client()
    key = ds.key('order', int(id))
    ds.delete(key)
