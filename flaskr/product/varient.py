# for graphql schema

import graphene
from collection import Collection


class Money(graphene.String):
    """A simple wrapper around String to represent Money, for demonstration."""


class DateTime(graphene.String):
    """A simple wrapper around String to represent DateTime, for demonstration."""


class UnsignedInt64(graphene.Int):
    """A simple wrapper around Int to represent UnsignedInt64, for demonstration."""

    # class ProductVariantContextualPricing(graphene.ObjectType):
    #     # Implement based on your pricing structure
    #     # This is just a placeholder
    #     pass

    # class DeliveryProfile(graphene.ObjectType):
    #     # Implement according to your delivery profile structure
    #     # Placeholder for demonstration
    #     pass

    # class Image(graphene.ObjectType):
    #     # Placeholder for image fields
    #     pass

    # class InventoryItem(graphene.ObjectType):
    # Placeholder for InventoryItem fields
    pass


class ProductVariantInventoryPolicy(graphene.Enum):
    # Add your enum values here
    ALLOW = 1
    DENY = 2


# class SelectedOption(graphene.ObjectType):
#     # Placeholder for SelectedOption fields
#     pass

# class Translation(graphene.ObjectType):
#     # Placeholder for Translation fields
#     pass


class ProductVariant(graphene.ObjectType):

    availableForSale = graphene.NonNull(graphene.Boolean)
    barcode = graphene.String()
    compareAtPrice = Money()
    createdAt = graphene.NonNull(DateTime)
    defaultCursor = graphene.NonNull(graphene.String)
    displayName = graphene.NonNull(graphene.String)
    id = graphene.NonNull(graphene.ID, description="The ID of the variant")
    inventoryPolicy = graphene.NonNull(ProductVariantInventoryPolicy)
    inventoryQuantity = graphene.Int()
    legacyResourceId = graphene.NonNull(UnsignedInt64)
    position = graphene.NonNull(graphene.Int)
    price = graphene.NonNull(Money)

    requiresComponents = graphene.NonNull(graphene.Boolean)

    sellableOnlineQuantity = graphene.NonNull(graphene.Int)
    sellingPlanGroupCount = graphene.NonNull(graphene.Int)
    sku = graphene.String()
    taxCode = graphene.String()
    taxable = graphene.NonNull(graphene.Boolean)
    title = graphene.NonNull(graphene.String,
                             description="The title of the variant")

    updatedAt = graphene.NonNull(DateTime)

    # metafield = graphene.Field(lambda: Metafield)  # Assuming Metafield is defined elsewhere
    # contextualPricing = graphene.NonNull(ProductVariantContextualPricing)
    # deliveryProfile = graphene.Field(DeliveryProfile)
    # image = graphene.Field(Image)
    # inventoryItem = graphene.NonNull(InventoryItem)
    # product = graphene.NonNull(Product)
    # selectedOptions = graphene.NonNull(graphene.List(graphene.NonNull(SelectedOption)))
    # translations = graphene.NonNull(graphene.List(graphene.NonNull(Translation)))
