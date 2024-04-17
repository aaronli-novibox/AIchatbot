import graphene

# base type
from base_type import SEO, ProductStatus

# connection
from collection import Collection
from varient import ProductVariant
from publication import ProductPublication

# class ProductCompareAtPriceRange(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class ProductContextualPricing(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class Image(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class Media(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class ResourceFeedback(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class ProductOption(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class ProductPriceRangeV2(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class ProductCategory(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass

# class Translation(graphene.ObjectType):
#     # 根据实际需要定义字段
#     pass


class Product(graphene.ObjectType):

    availablePublicationCount = graphene.Int(required=True)

    createdAt = graphene.DateTime(required=True)
    defaultCursor = graphene.String(required=True)
    description = graphene.String(required=True)
    descriptionHtml = graphene.String(required=True)

    handle = graphene.String(required=True)
    hasOnlyDefaultVariant = graphene.Boolean(required=True)
    hasOutOfStockVariants = graphene.Boolean(required=True)
    id = graphene.ID(required=True)

    inCollection = graphene.Boolean(required=True)
    isGiftCard = graphene.Boolean(required=True)
    legacyResourceId = graphene.Int(required=True)

    onlineStorePreviewUrl = graphene.String()
    onlineStoreUrl = graphene.String()
    options = graphene.List(graphene.String)

    productType = graphene.String(required=True)
    publicationCount = graphene.Int(required=True)
    publishedAt = graphene.DateTime()

    seo = graphene.Field(SEO)
    tags = graphene.List(graphene.String, required=True)
    templateSuffix = graphene.String()
    title = graphene.String(required=True)
    totalInventory = graphene.Int(required=True)
    totalVariants = graphene.Int(required=True)
    tracksInventory = graphene.Boolean(required=True)

    updatedAt = graphene.DateTime(required=True)

    vendor = graphene.String(required=True)

    # connection
    variants = graphene.Field(ProductVariant)
    collections = graphene.List(graphene.Field(Collection))
    resourcePublications = graphene.Field(
        ProductPublication)    # Placeholder for actual type

    # object，大概率是存在相互的关系或者是静态资源文件夹
    # featuredImage = graphene.Field(Image)
    # feedback = graphene.Field(
    #     lambda: ResourceFeedback)    # Placeholder for actual feedback type
    # images = graphene.List(graphene.Field(Image))
    # metafield = graphene.Field(
    #     lambda: Metafield)    # Assuming Metafield is defined elsewhere
    # priceRange = graphene.Field(
    #     lambda: ProductPriceRange)    # Placeholder for actual price range type

    # resourcePublicationOnCurrentPublication = graphene.Field(
    #     lambda: Publication)    # Placeholder
    # unpublishedPublications = graphene.Field(
    #     lambda: Publication)    # Placeholder for actual type
