#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Mangaa provides a simpler way for working with a MongoDB database.

Heavily modified from Wladston Viana's Manga
Copyright (c) 2015, Jingchao Hu
"""


import time
import pickle
import logging
import functools
import traceback

# Python.
from re import compile
from datetime import datetime
from collections import OrderedDict

# Pymongo.
from pymongo.cursor import Cursor
from pymongo import MongoClient
from pymongo.son_manipulator import SONManipulator
from bson.objectid import ObjectId


__author__ = 'Jingchao Hu'
__version__ = '0.2.4'
__license__ = 'MIT'

log = logging.getLogger('mangaa')
connection = None
db = None
_manipulators = []


# MongoDB will not store dates with milliseconds.
def milli_trim(x):
    return x.replace(
        microsecond=int((x.microsecond / 1000) * 1000))


def setup(mongodb_url='mongodb://localhost:27017/test'):
    global db, connection, _manipulators

    if db:
        log.warning('Database is already configured')

    database = mongodb_url.rsplit('/', 1)[-1]
    connection = MongoClient(mongodb_url)
    db = connection[database]

    for x in _manipulators:
        if hasattr(x.cls, '_indexes'):
            for indexlist, kwargs in x.cls._indexes:
                try:
                    db[x.cls_name].ensure_index(indexlist, **kwargs)
                except:
                    pass

        if hasattr(x.cls, '_shardkey'):
            try:
                connection.admin.command('enableSharding', database)
            except Exception as e:
                if 'already' in str(e):
                    try:
                        connection.admin.command(
                            'shardCollection',
                            '{}.{}'.format(database, x.cls_name),
                            key=dict(x.cls._shardkey))
                    except Exception as e:
                        if 'already' not in str(e):
                            log.warning('create shardkey failed, '
                                        'if you are developping'
                                        ', it is probably ok for that')
                            traceback.print_exc()

                else:
                    log.warning('create shardkey failed, '
                                'if you are developping'
                                ', it is probably ok')
                    traceback.print_exc()
        db.add_son_manipulator(x)

    return db


class _ModelManipulator(SONManipulator):

    '''
    Generates on-the-fly manipulators for newly registered models. Keeps track
    of collections already registered, to avoid double registration.
    '''

    _M01 = "Manipulator for collection {} was already defined."
    registered_collections = []

    def __init__(self, cls):
        self.cls = cls
        self.cls_name = cls.__name__.lower()

        if self.cls_name in self.registered_collections:
            raise Exception(self._M01.format(self.cls_name))

        else:
            self.registered_collections.append(self.cls_name)

    def transform_outgoing(self, son, collection):
        if son and self.cls_name == collection.name:
            return self.cls(son=son)

        else:
            return son


class MangaException(Exception):
    pass


class ValidationError(MangaException):

    def __init__(self, cls, attr, val):
        self.cls = cls
        self.attr = attr
        self.val = val

    def __str__(self):
        return "{}: trying to set {} <- {}:{}" \
            "".format(self.cls, self.attr,
                      type(self.val), self.val)


class DeserializationError(MangaException):

    def __init__(self, field, val):
        self.fld = field
        self.val = val

    def __str__(self):
        msg = "Can't deserialize value for field {}: {}"
        return msg.format(self.fld, self.val)


class ModelType(type):

    """
    This is a type that generates Model classes properly, setting their
    attributes not to be instances of Field, but rather an API for MongoDB
    itself.
    """

    @staticmethod
    def get_maker(attr):
        def getter(cls, attr=attr):
            return cls._fields[attr].to_python(cls._data.get(attr))

        return getter

    @staticmethod
    def set_maker(attr):
        def setter(cls, val=None, attr=attr):
            cls._data[attr] = cls._fields[attr].to_storage(val)
            # we don't validate on setting
            # we only validate on saving

        return setter

    def __new__(cls, name, bases, dct):
        dct.setdefault('_fields', {})
        dct.setdefault('_collection', name.lower())

        for x in bases:
            dct['_fields'].update(getattr(x, '_fields', {}))

        for attr, val in list(dct.items()):
            if attr == 'meta':
                if 'idformat' in val:
                    dct['_idformat'] = val['idformat']
                if 'unique' in val:
                    dct['_unique'] = val['unique']
                if 'indexes' in val:
                    dct['_indexes'] = val['indexes']
                if 'shardkey' in val:
                    dct['_shardkey'] = val['shardkey']
            elif isinstance(val, Field):
                dct['_fields'][attr] = val
                dct[attr] = property(cls.get_maker(attr), cls.set_maker(attr))

        rich_cls = super(ModelType, cls).__new__(cls, name, bases, dct)

        if any([hasattr(x, 'save') for x in bases]):
            if db:
                db.add_son_manipulator(_ModelManipulator(rich_cls))

            else:
                _manipulators.append(_ModelManipulator(rich_cls))

        return rich_cls


class Field(object):

    '''Base field for all fields.'''

    def __init__(self, default=None, blank=True):
        self.blank = blank
        self.default = default

    def validate(self, value):
        if not self.blank:
            assert value, 'field {} got value {}'.format(self, value)

    def pre_save_val(self, value):
        return None

    @staticmethod
    def to_storage(value):
        return value

    @staticmethod
    def to_python(value):
        return value


class SequenceField(Field):

    ''' Auto Increment integer field '''

    def __init__(self, name='default', default=None, blank=False):
        self.name = name
        self.blank = blank
        self.default = default

    def validate(self, value):
        assert isinstance(value, int)

    def pre_save_val(self, value):
        if value:
            return value

        while True:
            try:
                r = db.counters.find_and_modify(
                    query={'_id': self.name},
                    update={'$inc': {'seq': 1}},
                    new=True, upsert=True)
            except:
                continue
            else:
                break
        return r['seq']


class ObjectIdField(Field):

    def validate(self, value):
        assert isinstance(value, ObjectId)

        if not self.blank:
            assert value


class IntField(Field):

    def __init__(self, default=None, **kwargs):
        super(IntField, self).__init__(default, **kwargs)

    def validate(self, value):
        assert value is None or isinstance(value, int)

        if not self.blank:
            assert value is not None


class BooleanField(Field):

    def __init__(self, default=None, **kwargs):
        super(BooleanField, self).__init__(default, **kwargs)

    def validate(self, value):
        assert value is None or isinstance(value, bool)

        if not self.blank:
            assert value is not None


class FloatField(Field):

    def __init__(self, default=None, **kwargs):
        super(FloatField, self).__init__(default, **kwargs)

    def validate(self, value):
        assert value is None or \
            isinstance(value, int) or isinstance(value, float)

        if not self.blank:
            assert value is not None


class StringField(Field):

    def __init__(self, default='', length=None, **kwargs):
        super(StringField, self).__init__(default, **kwargs)

        self.length = length

    def validate(self, value):
        assert value is None or isinstance(value, str)

        if not self.blank:
            assert value.strip()

        if self.length:
            length = len(value.strip())

            assert length >= self.length[0] and length <= self.length[1]

    @staticmethod
    def to_storage(value):
        return value.strip() if value is not None else value


class EmailField(StringField):
    email_re = compile(r'^[\S]+@[\S]+\.[\S]+$')

    def __init__(self, default='', length=(5, 100), **kwargs):
        super(EmailField, self).__init__(default, length, **kwargs)

    def validate(self, value):
        super(EmailField, self).validate(value)

        if not self.email_re.match(value):
            raise AssertionError


class DateTimeField(Field):

    def __init__(self, default=None, blank=False, auto=None, **kwargs):
        super(DateTimeField, self).__init__(default, blank, **kwargs)

        self.auto = auto
        self.blank = blank

        if auto in ['modified', 'created']:
            self.default = lambda: datetime.utcnow()

    def validate(self, value):
        super(DateTimeField, self).validate(value)
        if not self.blank:
            assert isinstance(value, datetime) or value is None

    def pre_save_val(self, value):
        return datetime.utcnow() if self.auto == 'modified' else None

    @staticmethod
    def to_storage(value):
        try:
            return milli_trim(value) if value else None
        except:
            return value


class DictField(Field):

    def __init__(self, default=None, **kwargs):

        super(DictField, self).__init__(default or {}, **kwargs)

    def validate(self, value):
        assert isinstance(value, dict), 'value {}'.format(value)

        if not self.blank:
            assert value != {}


class DocumentField(Field):

    def __init__(self, default=None, document=None, **kwargs):
        super(DocumentField, self).__init__(default, **kwargs)

        self.document_class = document

    def validate(self, value):
        if not self.blank:
            assert value

        if value:
            assert isinstance(value, self.document_class)
            value.validate()

        else:
            assert value is None

    @staticmethod
    def to_storage(value):
        return getattr(value, '_data', None)

    def to_python(self, value):
        return self.document_class(son=value)


class ListField(Field):

    def __init__(self, default=None, field=None, **kwargs):
        default = default or []

        super(ListField, self).__init__(default, **kwargs)

        self.field = field

    def validate(self, value):
        assert isinstance(value, list)

        if not self.blank:
            assert value

        [self.field.validate(v) for v in value if self.field]

    def to_storage(self, value):
        if self.field:
            return [self.field.to_storage(v) for v in value]

        else:
            return value

    def to_python(self, value):
        if value is None:
            return []

        if not isinstance(value, list):
            raise DeserializationError(self, value)

        if self.field:
            return [self.field.to_python(v) for v in value]

        else:
            return value


class Document(object, metaclass=ModelType):

    '''
    A MongoDB storable document, without interface to persistant storage. It's
    the base class for Models (with do have persistance) and also embedded
    documents.
    '''
    # whether doc with undefined fields are allowed to be saved
    _flexible = False

    def __init__(self, data=None, son=None):
        self._data = {}
        validate_exempt = []

        for fname, field in list(self._fields.items()):
            if son and fname in son:
                # val is recovered for validation only.
                val = field.to_python(son.get(fname))

            elif data and fname in data:
                val = data[fname]

            else:
                val = field.default
                val = val() if callable(val) else val

            # Field skips validation if value does not come from son AND no
            # value is given for initialization.
            if son or not val:
                validate_exempt.append(fname)

            val_storage = son.get(fname) if son else field.to_storage(val)

            self._data[fname] = val_storage

        # fields that not specified, "flexible fields"
        if data:
            for fname in set(data.keys()) - set(self._fields.keys()):
                setattr(self, fname, data[fname])

        if son:
            for fname in set(son.keys()) - set(self._fields.keys()):
                setattr(self, fname, son[fname])

        self.validate(exclude=validate_exempt)

    def validate(self, exclude=None):
        exclude = exclude if exclude else []
        fields = [x for x in self._fields.items() if x[0] not in exclude]

        for fieldname, fieldinstance in fields:
            if fieldname == '_id':
                continue

            try:
                python_val = fieldinstance.to_python(self._data[fieldname])
                fieldinstance.validate(python_val)

            except AssertionError:
                val = self._data[fieldname]

                raise ValidationError(self.__class__.__name__, fieldname, val)


class Model(Document, metaclass=ModelType):

    '''Base class for all classes.'''

    # The _id field is required, nevertheless its blank attribute is True.
    # The _id is automatically generated by MongoDB, and doesn't need to be
    # provided.
    _id = Field(blank=True)

    @classmethod
    def _get_db(cls):
        return db

    @classmethod
    def _get_collection(cls):
        return db[cls._collection]

    def _get_document(self):
        if self._flexible:
            data = self._data.copy()
            for key, value in self.__dict__.items():
                if key != '_data':
                    data[key] = value
        else:
            data = self._data

        return data

    def _set_id(self):
        """ Delete or Format _id as required """
        doc = self._get_document()

        if hasattr(self, '_idformat') and self._idformat:
            doc['_id'] = self._idformat.format(**doc)

        if '_id' in doc and doc['_id'] is None:
            del doc['_id']

    @classmethod
    def cached(cls, timeout=60, cache_none=False):
        """ Cache queries

        :param timeout: cache timeout
        :param cache_none: cache None result

        Usage::

        >>> Model.cached(60).find_one({...})
        """
        return CachedModel(cls=cls, timeout=timeout, cache_none=cache_none)

    @classmethod
    def find(cls, *args, **kwargs):
        return db[cls._collection].find(*args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        return db[cls._collection].find_one(*args, **kwargs)

    @classmethod
    def remove(cls, *args, **kwargs):
        log.warning('Deprecated since pymongo 3.0')
        return db[cls._collection].remove(*args, **kwargs)

    @classmethod
    def delete_one(cls, *args, **kwargs):
        return db[cls._collection].delete_one(*args, **kwargs)

    @classmethod
    def delete_many(cls, *args, **kwargs):
        return db[cls._collection].delete_many(*args, **kwargs)

    def delete(self):
        if self._id:
            db[self._collection].delete_one({'_id': self._id})

            self._id = None

        else:
            raise Exception

    def save(self):
        for fieldname, fieldinstance in list(self._fields.items()):
            value = fieldinstance.pre_save_val(self._data.get(fieldname))

            if value:
                setattr(self, fieldname, value)

        self.validate()

        if self._id:
            spec = {'_id': self._id}
            doc = self._get_document()
            db[self._collection].update_one(spec, {'$set': doc}, upsert=True)

        else:
            self._set_id()
            doc = self._get_document()
            r = db[self._collection].insert_one(doc)
            self._data['_id'] = r.inserted_id

    def upsert(self):
        """ 根据Unique字段自动更新/插入Doc

        注意: 默认字段只在插入时有效, 更新时不会更新为默认字段,
        如确定要重置成默认字段, 请用Update更新
        """
        on_updates = {}
        on_inserts = {}
        for fieldname, fieldinstance in list(self._fields.items()):
            if fieldname != '_id':
                if self._data[fieldname] == fieldinstance.default:
                    on_inserts[fieldname] = self._data[fieldname]
                else:
                    on_updates[fieldname] = self._data[fieldname]

            value = fieldinstance.pre_save_val(self._data.get(fieldname))

            if value:
                setattr(self, fieldname, value)

        # update from flexible fields
        if self._flexible:
            for key, value in self.__dict__.items():
                if key != '_data':
                    on_updates[key] = value

        self.validate()
        self._set_id()

        spec = {}
        if '_id' in self._data and self._data['_id'] is not None:
            spec = {'_id': self._data['_id']}

        for key in getattr(self, '_unique', []):
            spec[key] = self._data[key]

        op = {'$set': on_updates}
        if on_inserts:
            op['$setOnInsert'] = on_inserts

        r = db[self._collection].find_one_and_update(spec, op, upsert=True)
        if not r and not self._data.get('_id'):
            r = db[self._collection].find_one(spec)
            self._data['_id'] = r._id

    def update(self, update_dict):
        """ 更具Unique字段更新update_dict

        update_dict必须包括$set, $push等mongodb更新操作符
        这里不做任何validation
        """
        self._set_id()

        spec = {}
        for key in self._unique:
            spec[key] = self._data[key]

        db[self._collection].update_one(spec, update_dict)

    @classmethod
    def upsert_bulk(cls, docs, on_insert=False):
        """ 根据Unique字段更新docs, 批量执行 """
        op = db[cls._collection].initialize_unordered_bulk_op()
        for doc in docs:
            assert isinstance(doc, cls)
            spec = {}
            for key in cls._unique:
                spec[key] = getattr(doc, key)
            if '_id' in doc._data and doc._data['_id'] is None:
                del doc._data['_id']
            setop = '$setOnInsert' if on_insert else '$set'
            data = doc._get_document()
            op.find(spec).upsert().update({setop: data})
        op.execute()

    @classmethod
    def update_bulk(cls, docs, update_dict):
        """ 根据Unique字段更新update_dict, 批量执行 """
        op = db[cls._collection].initialize_unordered_bulk_op()
        for doc in docs:
            assert isinstance(doc, cls)
            spec = {}
            for key in cls._unique:
                spec[key] = getattr(doc, key)
            if '_id' in doc._data and doc._data['_id'] is None:
                del doc._data['_id']
            op.find(spec).update(update_dict)
        op.execute()

    @classmethod
    def raw_update(cls, *args, **kwargs):
        log.warning('Deprecated since pymongo 3.0')
        return db[cls._collection].update(*args, **kwargs)


class FlexibleModel(Model):

    """ A Model that allows undefined field values.

    An otherwise *strict* model will refuse to save any undefined value
    """
    _flexible = True


class CachedModel(object):

    """ Used in Model.cached """
    caches = {}

    def __init__(self, cls, timeout, cache_none):
        self.cls = cls
        self.timeout = timeout
        self.cache_none = cache_none
        self.count = 0
        if self.cls not in self.caches:
            self.caches[self.cls] = {}

    def _clear_timeout(self):
        cache = self.caches[self.cls]
        now = time.time()
        invals = []
        for key, values in cache.items():
            if values[0] < now - self.timeout:
                invals.append(key)
        for key in invals:
            del cache[key]

    def __getattr__(self, name):
        self.count += 1
        if self.count % 1000 == 0:
            self._clear_timeout()

        attr = getattr(self.cls, name)
        if callable(attr):
            # wrap this callable to use cache
            @functools.wraps(attr)
            def deco(*args, **kwargs):
                cache = self.caches[self.cls]
                args = [OrderedDict(sorted(x.items()))
                        if isinstance(x, dict) else x
                        for x in args]
                kwargs = OrderedDict(sorted(kwargs.items()))
                key = pickle.dumps([attr.__name__, args, kwargs])
                cache_miss = key not in cache

                def timedout():
                    return cache[key][0] < time.time() - self.timeout

                if cache_miss or timedout():
                    value = attr(*args, **kwargs)
                    if isinstance(value, Cursor):
                        # this will consume A LOT of memory, use with care
                        value = list(value)
                    if value is not None or self.cache_none:
                        cache[key] = (time.time(), value)
                    else:
                        return
                return cache[key][1]
            return deco
        else:
            return attr
