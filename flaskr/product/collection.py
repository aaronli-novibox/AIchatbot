import graphene
from base_type import SEO

# class Image(graphene.ObjectType):
#     # 假设包含图像的基本字段，如src
#     src = graphene.String(description="The URL of the image.")

# class ResourceFeedback(graphene.ObjectType):
#     # 根据需要定义feedback的具体结构
#     messages = graphene.List(graphene.String, description="Feedback messages.")

# class CollectionRuleSet(graphene.ObjectType):
#     # 定义smart collection的规则集
#     # 例如，可以包含规则类型和匹配值
#     applied_rule = graphene.String(
#         description="Applied rule for including products in the collection.")


class CollectionSortOrder(graphene.Enum):
    MANUAL = "MANUAL"
    BEST_SELLING = "BEST_SELLING"
    ALPHA_ASC = "ALPHA_ASC"
    ALPHA_DESC = "ALPHA_DESC"
    PRICE_DESC = "PRICE_DESC"
    PRICE_ASC = "PRICE_ASC"
    CREATED_DESC = "CREATED_DESC"
    CREATED_ASC = "CREATED_ASC"


class Collection(graphene.ObjectType):
    availablePublicationCount = graphene.Int(
        required=True,
        description="The number of publications without feedback errors.")
    description = graphene.String(
        required=True, description="Text-only description stripped of HTML.")

    handle = graphene.String(
        required=True,
        description="A unique string identifier for the collection.")
    hasProduct = graphene.Boolean(
        required=True,
        description="Whether the collection includes a specified product.")
    id = graphene.ID(required=True, description="A globally-unique ID.")

    legacyResourceId = graphene.Int(required=True,
                                    description="ID in the REST Admin API.")

    productsCount = graphene.Int(
        required=True, description="The number of products in the collection.")
    publicationCount = graphene.Int(
        required=True,
        description=
        "The number of publications on which the resource is published.")
    publishedOnCurrentPublication = graphene.Boolean(
        required=True,
        description="Resource published status on the calling app's publication."
    )
    publishedOnPublication = graphene.Boolean(
        required=True,
        description="Resource published status on a given publication.")

    seo = graphene.Field(SEO,
                         required=True,
                         description="SEO information of the collection.")
    sortOrder = graphene.Field(
        CollectionSortOrder,
        required=True,
        description="Default sort order in the admin and sales channels.")
    templateSuffix = graphene.String(
        description="Suffix of the Liquid template used.")
    title = graphene.String(required=True,
                            description="The name of the collection.")
    translations = graphene.List(
        graphene.String,
        required=True,
        description="Translations associated with the collection.")
    updatedAt = graphene.DateTime(
        required=True, description="When the collection was last modified.")

    #

    # feedback = graphene.Field(
    #     ResourceFeedback,
    #     description="Feedback provided through resource feedback.")
    # rule_set = graphene.Field(CollectionRuleSet,
    #                           description="Rules for smart collections.")
    # metafield = graphene.Field(
    #     Metafield, description="Returns a metafield by namespace and key.")
    # image = graphene.Field(
    #     Image, description="The image associated with the collection.")
    # description_html = graphene.String(
    #     required=True, description="Description including HTML formatting.")
