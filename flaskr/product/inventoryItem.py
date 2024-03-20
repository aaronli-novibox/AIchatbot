import graphene
from varient import ProductVariant
from base_type import CountryCode
from inventoryLevel import InventoryLevel

# class MoneyV2(graphene.ObjectType):
#     # 假设包含金额和货币
#     amount = graphene.Float(description="Amount of money.")
#     currency_code = graphene.String(description="Currency code.")


class InventoryItem(graphene.ObjectType):
    countryCodeOfOrigin = graphene.Field(CountryCode)
    createdAt = graphene.DateTime(required=True)
    duplicateSkuCount = graphene.Int(required=True)
    harmonizedSystemCode = graphene.String()
    id = graphene.ID(required=True)
    inventoryHistoryUrl = graphene.String()
    inventoryLevel = graphene.Field(InventoryLevel)
    legacyResourceId = graphene.Int(required=True)
    locationsCount = graphene.Int(required=True)
    provinceCodeOfOrigin = graphene.String()
    requiresShipping = graphene.Boolean(required=True)
    sku = graphene.String(unique=True)
    tracked = graphene.Boolean(required=True)
    updatedAt = graphene.DateTime(required=True)
    variant = graphene.Field(ProductVariant, required=True)

    # unit_cost = graphene.Field(MoneyV2)
    # tracked_editable = graphene.Field(EditableProperty, required=True)
