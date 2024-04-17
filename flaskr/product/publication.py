import graphene
from product import Product


class Channel(graphene.ObjectType):
    id = graphene.ID(required=True,
                     description="A globally-unique ID for the channel.")
    name = graphene.String(required=True,
                           description="The name of the channel.")
    supportsFuturePublishing = graphene.Boolean(
        required=True,
        description="Whether the channel supports future publishing.")
    hasCollection = graphene.Boolean(
        required=True,
        description="Whether the collection is available to the channel.")


class ProductPublication(graphene.ObjectType):
    channel = graphene.Field(
        Channel,
        required=True,
        description="The channel where the product was or is published.")
    isPublished = graphene.Boolean(
        required=True,
        description="Whether the publication is published or not.")
    publishDate = graphene.DateTime(
        description=
        "The date that the product was or is going to be published on the channel."
    )
    product = graphene.Field(
        lambda: Product,
        required=True,
        description=
        "The product that was or is going to be published on the channel.")


# class ResourcePublicationV2(graphene.ObjectType):
#     isPublished = graphene.Boolean(
#         required=True,
#         description=
#         "Whether the resource publication is published. If true, then the resource publication is published to the publication. If false, then the resource publication is staged to be published to the publication."
#     )
#     publication = graphene.Field(
#         ,
#         required=True,
#         description="The publication the resource publication is published to.")
#     publishDate = graphene.DateTime(
#         description=
#         "The date that the resource publication was or is going to be published to the publication."
#     )
# publishable = graphene.Field(
#     Publishable,
#     required=True,
#     description="The resource published to the publication.")

# 为了使GraphQL能够正确处理Publishable接口，需要告诉它如何根据类型解析这个接口
# def resolve_publishable_type(publishable, info):
#     # 这里的实现应该基于publishable实例的具体类型来返回对应的GraphQL类型
#     # 例如，如果publishable是Product的实例，那么应该返回Product类型
#     # 这里只是一个简化的示例，实际逻辑可能更复杂
#     return Product

# class Query(graphene.ObjectType):
#     resource_publication = graphene.Field(
#         ResourcePublicationV2,
#         id=graphene.ID(
#             required=True,
#             description="The ID of the resource publication to query."))

#     def resolve_resource_publication(self, info, id):
#         # 根据id查询并返回资源发布信息的示例实现，实际实现需要访问数据存储
#         return ResourcePublicationV2(
#             isPublished=True,
#             publication=Publication(id="1", name="Online Store"),
#             publishDate="2023-01-01T00:00:00Z",
#             publishable=Product(id="1", title="Example Product"))

# schema = graphene.Schema(query=Query,
#                          types=[Product],
#                          type_resolver=resolve_publishable_type)
