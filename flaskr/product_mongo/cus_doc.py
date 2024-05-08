from mongoengine import Document, ValidationError, EmbeddedDocument, LazyReferenceField, EmbeddedDocumentField, ReferenceField, DoesNotExist, StringField, ListField


def get_or_create(cls, defaults=None, **kwargs):
    try:
        # Try to find a document matching the provided kwargs

        # pprint(kwargs)
        if "shopify_id" in kwargs.keys():
            instance = cls.objects.get(shopify_id=kwargs["shopify_id"])
            print(instance)
            # for key, value in kwargs.items():
            #     print(key)
            #     instance.modify(upsert=True, **{key: value})

            # print(kwargs)
            instance.modify(upsert=True, **kwargs)
            return instance, False
        else:
            return cls(**kwargs), False
    except DoesNotExist:
        # If no document matches, create a new one with kwargs and defaults

        if defaults:
            kwargs.update(defaults)

            # debug
            # for key, val in kwargs.items():
            #     print(cls._fields.get(key))
            # obj = cls(**{key: val})
        obj = cls(**kwargs)
        obj.save(validate=False)
        return obj, True

    except ValidationError as e:
        print("ValidationError occurred:", e)
        print("Problematic data:", kwargs)
        raise    # 再次抛出异常以便于调用方处理


def recursive_get_or_create(cls, data):
    """
    递归获取或创建文档
    data: dict, 数据
    """

    processed_data = {}
    for field_name, field_value in data.items():

        field = cls._fields.get(field_name)

        if isinstance(field,
                      (LazyReferenceField, EmbeddedDocumentField,
                       ReferenceField)) and isinstance(field_value, dict):
            # For EmbeddedDocumentField, create an embedded document directly
            # For LazyReferenceField, perform recursive get_or_create

            ref_cls = field.document_type
            doc, created = ref_cls.recursive_get_or_create(
                field_value) if hasattr(
                    ref_cls,
                    'recursive_get_or_create') else ref_cls.get_or_create(
                        **field_value)
            processed_data[field_name] = doc
        elif isinstance(field, ListField) and isinstance(
                field.field,
            (LazyReferenceField, EmbeddedDocumentField,
             ReferenceField)) and field_value is not None and all(
                 isinstance(item, dict) for item in field_value):

            # Handle lists of documents
            ref_cls = field.field.document_type    # Get the document type of the items in the list
            list_data = []
            for item in field_value:
                if hasattr(ref_cls, 'recursive_get_or_create'):
                    doc, created = ref_cls.recursive_get_or_create(item)
                else:
                    doc, created = ref_cls.get_or_create(**item)
                list_data.append(doc)
            processed_data[field_name] = list_data
        else:
            # Directly assign the value for other field types
            processed_data[field_name] = field_value

    # Try to get or create the document with the processed data
    return cls.get_or_create(**processed_data)


Document.get_or_create = classmethod(get_or_create)
Document.recursive_get_or_create = classmethod(recursive_get_or_create)
EmbeddedDocument.get_or_create = classmethod(get_or_create)
EmbeddedDocument.recursive_get_or_create = classmethod(recursive_get_or_create)
